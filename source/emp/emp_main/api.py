#!/usr/bin/env python3
"""
Definition of EMP REST API.

This API is all syncronous as the Django ORM and Middlewares are not async yet.
Django recommends to limit switching from async to sync, and as the ASGI is
used for access with keep it sync afterwards. See:
https://docs.djangoproject.com/en/3.2/topics/async/
"""
import json
import logging
from typing import List

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.forms.models import model_to_dict
from django.http import HttpResponse
from ninja import NinjaAPI
from ninja import Query
from ninja import Schema
from ninja.renderers import BaseRenderer

from esg.models.datapoint import DatapointById
from esg.models.datapoint import DatapointList
from esg.models.datapoint import DatapointType
from esg.models.datapoint import DatapointDataFormat
from esg.models.request import HTTPError
from esg.services.base import RequestInducedException

from .models import Datapoint as DatapointDb

logger = logging.getLogger(__name__)


class JSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return json.dumps(data)


api = NinjaAPI(
    title="EMP API", version="v1", docs_url="/", renderer=JSONRenderer()
)


class GenericDatapointRelatedView:
    """
    As of April 2022 django Ninja doesn't support class based views.
    See: https://github.com/vitalik/django-ninja/issues/15

    This is a simple class that encapuslates the generic logic.
    """

    DatapointModel = DatapointDb
    RelatedModel = None
    list_response_model = None
    list_latest_response_model = None
    list_at_interval_response_model = None
    create_response_model = None
    update_response_model = None

    class DatapointFilterParams(Schema):
        """
        Define filter possibilities for datapoints.
        Note the keys must match something expect by `django.QuerySets.filter`.
        See: https://docs.djangoproject.com/en/4.0/ref/models/querysets/#filter
        """

        id__in: List[int] = None
        origin__exact: str = None
        origin__regex: str = None
        origin_id__in: List[str] = None
        origin_id__regex: str = None
        short_name__regex: str = None
        type__exact: DatapointType = None
        data_format__in: List[DatapointDataFormat] = None
        description__regex: str = None
        unit__regex: str = None

    def _handle_exceptions(method):
        """
        A little decorator that handles exceptions and transforms those into
        the output expected by Ninja.
        """

        def handle_exceptions(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except RequestInducedException as exception:
                http_error = HTTPError(detail=exception.detail)
                return HttpResponse(
                    http_error.json(),
                    status=400,
                    content_type="application/json",
                )
            except Exception:
                logger.exception("Caught exception during handling request.")
                http_error = HTTPError(
                    detail=(
                        "This is an internal server error and there is likely "
                        "nothing you can do about it. Please contact your "
                        "service provider."
                    )
                )
                return HttpResponse(
                    http_error.json(),
                    status=500,
                    content_type="application/json",
                )

        return handle_exceptions

    def get_filtered_datapoints(self, datapoint_filter_params):
        """
        Return a queryset of datapoints matching the requested filter
        parameters.

        Arguments:
        ----------
        datapoint_filter_params: instance of `DatapointFilterParams`
            Defines the filters that should be applied to the datapoints.
        """
        active_filters = {}
        for filter_key, filter_value in datapoint_filter_params:
            if filter_value is None:
                continue
            active_filters[filter_key] = filter_value
        datapoints = self.DatapointModel.objects.all().filter(**active_filters)
        return datapoints

    @_handle_exceptions
    def list_latest(self, request, datapoint_filter_params={}):
        """
        Return the latest state of metadata of zero or more datapoints matching
        the requested filter parameters.

        Arguments:
        ----------
        datapoint_filter_params: instance of `DatapointFilterParams`
            Defines the filters that should be applied to the datapoints.
        Returns:
        --------
        http_response: django.http.HttpResponse
            The requested datapoints as JSON string.
        """
        datapoints = self.get_filtered_datapoints(datapoint_filter_params)

        # Group by datapoint ID.
        content_as_dict = {}
        for datapoint in datapoints:
            content_as_dict[str(datapoint.id)] = model_to_dict(datapoint)

        # Convert to jsonable, skip validation.
        content_pydantic = DatapointById.construct_recursive(
            __root__=content_as_dict
        )
        content = content_pydantic.json()

        return HttpResponse(
            content, status=200, content_type="application/json"
        )

    @_handle_exceptions
    def update_latest(self, request, datapoints):
        """
        Update or create the latest state of datapoint metadata.

        The matching between the provided data and the existing datapoints is
        the following:
        * If the ID field of a `Datapoint` object is not `null` it is
          assumed that the datapoint with this ID should be updated.
        """
        created_datapoints = []
        non_existing_datapoint_ids = []
        for datapoint in datapoints.__root__:
            dp_dict = datapoint.dict()
            if dp_dict["id"]:
                # If `id` is not None assume there is a datapoint that should
                # be updated.
                try:
                    dp_db = DatapointDb.objects.get(id=dp_dict["id"])
                except DatapointDb.DoesNotExist:
                    non_existing_datapoint_ids.append(dp_dict["id"])
                    continue
            elif dp_dict["origin"] and dp_dict["origin_id"]:
                # If `id` is None but both `origin` and `origin_id` fields
                # are not None we use these fields to check for an existing
                # datapoint and create a new one if that doesn't exist.
                try:
                    dp_db = DatapointDb.objects.get(
                        origin=dp_dict["origin"], origin_id=dp_dict["origin_id"]
                    )
                except DatapointDb.DoesNotExist:
                    dp_db = DatapointDb(**dp_dict)

            else:
                # As a last resort: Create a new datapoint if we have neither
                # `id` nor `origin` and `origin_id`.
                dp_db = DatapointDb(**dp_dict)

            # Now update all the fields for the case that the datapoint
            # existed already. This shouldn't be too expensive in case the
            # datapoint has been created, as everything is still in memory.
            for field, value in dp_dict.items():
                # Don't update `id`, it would be set to None in certain
                # conditions which causes unique constraint failures.
                if field == "id":
                    continue
                setattr(dp_db, field, value)

            created_datapoints.append(dp_db)

        if non_existing_datapoint_ids:
            raise RequestInducedException(
                detail=(
                    "Aborting update/create due to unknown datapoint IDs: {}"
                    "".format(non_existing_datapoint_ids)
                )
            )

        # Now we know all datapoints are all right, save and prepare output.
        created_datapoints_by_id = {}
        for dp_db in created_datapoints:
            dp_db.save()
            created_datapoints_by_id[str(dp_db.id)] = model_to_dict(dp_db)

        created_datapoints_pydantic = DatapointById.construct_recursive(
            __root__=created_datapoints_by_id
        )

        # Publish updated datapoints in channel layer.
        # TODO: Make this parallel
        channel_layer = get_channel_layer()
        for dp_id in created_datapoints_pydantic.__root__:
            dp_pydantic = created_datapoints_pydantic.__root__[dp_id]
            dp_json = dp_pydantic.json()
            async_to_sync(channel_layer.group_send)(
                "datapoint.metadata.latest." + dp_id,
                {"type": "datapoint.related", "json": dp_json},
            )

        created_datapoints_json = created_datapoints_pydantic.json()
        return HttpResponse(
            created_datapoints_json, status=200, content_type="application/json"
        )


class DatapointView(GenericDatapointRelatedView):
    pass


dp_view = DatapointView()


@api.get(
    "/datapoint/metadata/latest/",
    response={200: DatapointById, 400: HTTPError, 500: HTTPError},
    tags=["Datapoint Metadata"],
    summary=" ",  # Deactivate summary.
)
def get_datapoint_latest(
    request,
    datapoint_filter_params: dp_view.DatapointFilterParams = Query(...),
):
    """
    Return a queryset of datapoints matching the requested filter
    parameters.
    """

    response = dp_view.list_latest(
        request=request, datapoint_filter_params=datapoint_filter_params
    )
    return response


@api.put(
    "/datapoint/metadata/latest/",
    response={200: DatapointList},
    tags=["Datapoint Metadata"],
    summary=" ",  # Deactivate summary.
)
def put_datapoint_latest(
    request, datapoints: DatapointList,
):
    """
    Update or create the latest state of datapoint metadata.

    The matching between the provided data and the existing datapoints is
    the following:
    * If the `id` field of a `Datapoint` object **is not** `null` it is
      assumed that the datapoint with this ID should be updated.
    * If the `id` field of a `Datapoint` object **is** `null` the combination
      of `origin` and `origin_id` is used look up a datapoint with identical
      values. If such a datapoint exists it is updated, else it is created.
    * If neither `id` nor **both** `origin` and `origin_id` are provided for a
      datapoint the datapoint is created.

    The following situations will result in an error (400):
    * If the `id` field of a `Datapoint` object **is not** `null` but no
      datapoint with that ID exists.

    **Finally note**: This operation is all or nothing. If you receive an
    error no data is written to DB.
    """
    response = dp_view.update_latest(request=request, datapoints=datapoints)
    return response


# @api.get(
#     "/datapoint/", response={200: DatapointById},
# )
# def get_datapoint(
#     request,
#     datapoint_filter_params: dp_view.DatapointFilterParams = Query(...),
# ):
#     """
#     Return the metadata of zero or more datapoints matching the
#     requested filter parameters.
#     """
#     response = dp_view.list(
#         request=request, datapoint_filter_params=datapoint_filter_params
#     )
#     return response
