#!/usr/bin/env python3
"""
Definition of EMP REST API.

This API is all syncronous as the Django ORM and Middlewares are not async yet.
Django recommends to limit switching from async to sync, and as the ASGI is
used for access with keep it sync afterwards. See:
https://docs.djangoproject.com/en/3.2/topics/async/

As of April 2022 django Ninja doesn't support class based views.
See: https://github.com/vitalik/django-ninja/issues/15
However, we still want to make parts of the API calls reusable. The logic in
this file is hence grouped in to `View` classes, quite similar to Django's
class based views. However, due to the limitation in Ninja, patching up
the methods to the NinjaAPI must happen outside this classes.
"""
from datetime import datetime
import logging
from typing import List

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.forms.models import model_to_dict
from django.http import HttpResponse
from ninja import NinjaAPI
from ninja import Query
from ninja import Schema
from pydantic import Field

from esg.models.datapoint import DatapointById
from esg.models.datapoint import DatapointList
from esg.models.datapoint import DatapointType
from esg.models.datapoint import DatapointDataFormat
from esg.models.datapoint import ValueMessageByDatapointId
from esg.models.datapoint import ValueMessageListByDatapointId
from esg.models.request import HTTPError
from esg.services.base import RequestInducedException

from .models import Datapoint as DatapointDb
from emp_main.models import ValueMessage as ValueHistoryDb
from emp_main.models import LastValueMessage as ValueLatestDb

logger = logging.getLogger(__name__)


api = NinjaAPI(title="EMP API", version="v1", docs_url="/",)


class GenericAPIView:
    """
    Some generic stuff that should be relevant for all API endpoints.
    """

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


class GenericDatapointAPIView(GenericAPIView):
    """
    Generic functionality for classes that interact with datapoints.

    NOTE: this class is not fully covered by the tests. Be extra careful
          if you change something and manually test if the filters work as
          expected afterwards.

    TODO: Add tests for`get_filtered_datapoints`, `build_active_filter_dict`
          and the `DatapointFilterParams` schema

    Attributes:
    -----------
    DatapointModel: django.db.models.Model
        The django model used to fetch/write datapoint metadata from/to db.
    DatapointFilterParams: ninja.Schema
        Define filter possibilities for datapoints.
        Note the keys must match something expect by `django.QuerySets.filter`.
        See: https://docs.djangoproject.com/en/4.0/ref/models/querysets/#filter
    """

    DatapointModel = DatapointDb

    class DatapointFilterParams(Schema):
        id__in: List[int] = Field(None, description="`Datapoint.id` in list")
        origin__exact: str = Field(
            None, description="`Datapoint.origin` exact match"
        )
        origin__regex: str = Field(
            None, description="`Datapoint.origin` regex match"
        )
        origin_id__in: List[str] = Field(
            None, description="`Datapoint.origin_id` in list"
        )
        origin_id__regex: str = Field(
            None, description="`Datapoint.origin_id` regex match"
        )
        short_name__regex: str = Field(
            None, description="`Datapoint.short_name` regex match"
        )
        # Use in here instead of exact as the List[] makes the field
        # not required in SwaggerUI.
        type__in: List[DatapointType] = Field(
            None, description="`Datapoint.type` in list"
        )
        data_format__in: List[DatapointDataFormat] = Field(
            None, description="`Datapoint.data_format` in list"
        )
        description__regex: str = Field(
            None, description="`Datapoint.description` regex match"
        )
        unit__regex: str = Field(
            None, description="`Datapoint.unit` regex match"
        )

    def build_active_filter_dict(self, filter_params):
        """
        Build a dict that can be forwarded to `django.QuerySets.filter`

        Arguments:
        ----------
        filter_params: instance of `ninja.Schema`
            A schema instance defining filter operations and values.
            E.g. `datapoint_filter_params` of `get_filtered_datapoints`

        Returns:
        --------
        active_filters: dict
            Has one key for every filter string for which the value is not
            None. Create a `isnull` filter if you must filter for objects
            with a None in a field.
        """
        active_filters = {}
        for filter_key, filter_value in filter_params:
            if filter_value is None:
                continue
            active_filters[filter_key] = filter_value
        return active_filters

    def get_filtered_datapoints(self, datapoint_filter_params):
        """
        Return a queryset of datapoints matching the requested filter
        parameters.

        Arguments:
        ----------
        datapoint_filter_params: instance of `DatapointFilterParams`
            Defines the filters that should be applied to the datapoints.
        """
        active_filters = self.build_active_filter_dict(datapoint_filter_params)
        datapoints = self.DatapointModel.objects.all().filter(**active_filters)
        return datapoints


class GenericDatapointRelatedAPIView(GenericDatapointAPIView):
    """
    Generic code for API classes for data that is related to a datapoint,
    e.g. by foreign key.

    This class assumes that the related data is stored in two seperate tables,
    one holding zero or one latest values per datapoint, and a second holding
    the historic values of the data.

    Subclass to use. Must set the following attributes.

    Attriubtes:
    -----------
    RelatedDataLatestModel: django.db.models.Model
        The django model that is used to save/load the latest known data
        item per datapoint.
    RelatedDataHistoryModel: django.db.models.Model
        The django model that is used to save/load the historic data
        items per datapoint.
    list_latest_response_model: esg.models.base._BaseModel
        The pydantic model that is used to serialize the latest data.
        This model must have a Dict as __root__ element which is set to
        the datapoint id.
    list_history_response_model: esg.models.base._BaseModel
        The pydantic model that is used to serialize the history data.
        This model must have a Dict as __root__ element which is set to
        the datapoint id.
    update_latest_response_model: esg.models.base._BaseModel
        The pydantic model that is used to serialize the cleaned and validated
        data that is sent back as confirmation for any an PUT update latest
        operation.
    """

    RelatedDataLatestModel = None
    RelatedDataHistoryModel = None
    list_latest_response_model = None
    list_history_response_model = None
    update_latest_response_model = None

    def list_latest(
        self, request, datapoint_filter_params, related_filter_params
    ):
        """
        Returns the latest data item per datapoint.
        """
        # TODO: Add test that list calls this method to fetch filtered
        #       datapoints, and of course that the query params are forewarded.
        datapoints = self.get_filtered_datapoints(datapoint_filter_params)

        related_data = self.RelatedDataLatestModel.objects.filter(
            datapoint__in=datapoints
        )

        # Filter by query parameters.
        # NOTE: If this filter is applied or not is not covered in the test.
        #       If you change someting in this block be extra careful and test
        #       manually afterwards.
        # TODO: Add tests that filter is applied.
        active_filters = self.build_active_filter_dict(related_filter_params)
        related_data = related_data.filter(**active_filters)

        # Group by datapoint ID.
        content_as_dict = {}
        for data_item in related_data:
            content_as_dict[str(data_item.datapoint.id)] = model_to_dict(
                data_item
            )

        # Convert to jsonable, skip validation.
        content_pydantic = self.list_latest_response_model.construct_recursive(
            __root__=content_as_dict
        )

        # At this point content contains additional fields (as extra fields
        # are not removed due to skipped validation). This removes the
        # extra fields, but may actually not be very nice.
        content_pydantic = self.list_latest_response_model.parse_raw(
            content_pydantic.json()
        )

        content = content_pydantic.json()

        return HttpResponse(
            content, status=200, content_type="application/json"
        )

    def list_history(
        self, request, datapoint_filter_params, related_filter_params
    ):
        """
        Returns the historic data item per datapoint.
        """
        datapoints = self.get_filtered_datapoints(datapoint_filter_params)

        related_data = self.RelatedDataHistoryModel.objects.filter(
            datapoint__in=datapoints
        )

        # Filter by query parameters.
        # NOTE: If this filter is applied or not is not covered in the test.
        #       If you change someting in this block be extra careful and test
        #       manually afterwards.
        # TODO: Add tests that filter is applied.
        active_filters = self.build_active_filter_dict(related_filter_params)
        related_data = related_data.filter(**active_filters)

        # Make a list of objects belonging to datapoint ID for each datapoint.
        content_as_dict = {}
        for data_item in related_data:
            dp_id = str(data_item.datapoint.id)
            data_items_datapoint = content_as_dict.get(dp_id, [])
            data_items_datapoint.append(model_to_dict(data_item))
            content_as_dict[dp_id] = data_items_datapoint

        # Convert to jsonable, skip validation.
        content_pydantic = self.list_history_response_model.construct_recursive(
            __root__=content_as_dict
        )

        # At this point content contains additional fields (as extra fields
        # are not removed due to skipped validation). This removes the
        # extra fields, but may actually not be very nice.
        content_pydantic = self.list_history_response_model.parse_raw(
            content_pydantic.json()
        )

        content = content_pydantic.json()

        return HttpResponse(
            content, status=200, content_type="application/json"
        )


##############################################################################
# Datapoint Value Messages -> /datapoint/value/*
##############################################################################


class DatapointValueAPIView(GenericDatapointRelatedAPIView):
    RelatedDataLatestModel = ValueLatestDb
    RelatedDataHistoryModel = ValueHistoryDb
    list_latest_response_model = ValueMessageByDatapointId
    list_history_response_model = ValueMessageListByDatapointId

    # This is defined here every time to adapt the field descriptions.
    # TODO: Add test that these filters are applicable to the target model.
    class ValueFilterParams(Schema):
        time__gte: datetime = Field(
            None, description="`ValueMessage.time` greater or equal this value."
        )
        time__lt: datetime = Field(
            None, description="`ValueMessage.time` less this value."
        )


dp_value_view = DatapointValueAPIView()


@api.get(
    "/datapoint/value/latest/",
    response={200: ValueMessageByDatapointId, 400: HTTPError, 500: HTTPError},
    tags=["Datapoint Value"],
    summary=" ",  # Deactivate summary.
)
def get_datapoint_value_latest(
    request,
    datapoint_filter_params: dp_value_view.DatapointFilterParams = Query(...),
    value_filter_params: dp_value_view.ValueFilterParams = Query(...),
):
    """
    Return the latest values for datapoints targeted by the filter.
    """

    response = dp_value_view.list_latest(
        request=request,
        datapoint_filter_params=datapoint_filter_params,
        related_filter_params=value_filter_params,
    )
    return response


@api.get(
    "/datapoint/value/history/",
    response={
        200: ValueMessageListByDatapointId,
        400: HTTPError,
        500: HTTPError,
    },
    tags=["Datapoint Value"],
    summary=" ",  # Deactivate summary.
)
def get_datapoint_value_history(
    request,
    datapoint_filter_params: dp_value_view.DatapointFilterParams = Query(...),
    value_filter_params: dp_value_view.ValueFilterParams = Query(...),
):
    """
    Return one or more value messages for datapoints targeted by the filter.
    """

    response = dp_value_view.list_history(
        request=request,
        datapoint_filter_params=datapoint_filter_params,
        related_filter_params=value_filter_params,
    )
    return response


##############################################################################
# Datapoint Metadata -> /datapoint/metadata/*
##############################################################################


class DatapointMetadataAPIView(GenericDatapointAPIView):
    """
    methods for handling calls to /datapoint/metadata/ endpoints.
    """

    @GenericAPIView._handle_exceptions
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
        # TODO: Add test that list calls this method to fetch filtered
        #       datapoints, and of course that the query params are forewarded.
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

    @GenericAPIView._handle_exceptions
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


dpm_view = DatapointMetadataAPIView()


@api.get(
    "/datapoint/metadata/latest/",
    response={200: DatapointById, 400: HTTPError, 500: HTTPError},
    tags=["Datapoint Metadata"],
    summary=" ",  # Deactivate summary.
)
def get_datapoint_metadata_latest(
    request,
    datapoint_filter_params: dpm_view.DatapointFilterParams = Query(...),
):
    """
    Return a queryset of datapoints matching the requested filter
    parameters.
    """

    response = dpm_view.list_latest(
        request=request, datapoint_filter_params=datapoint_filter_params
    )
    return response


@api.put(
    "/datapoint/metadata/latest/",
    response={200: DatapointList},
    tags=["Datapoint Metadata"],
    summary=" ",  # Deactivate summary.
)
def put_datapoint_metadata_latest(
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
    response = dpm_view.update_latest(request=request, datapoints=datapoints)
    return response
