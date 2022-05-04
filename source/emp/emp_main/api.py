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
from django.db import IntegrityError
from django.db import transaction
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from ninja import Path
from ninja import Query
from ninja import Schema
from pydantic import Field

from esg.models.datapoint import DatapointById
from esg.models.datapoint import DatapointList
from esg.models.datapoint import DatapointType
from esg.models.datapoint import DatapointDataFormat
from esg.models.datapoint import PutSummary
from esg.models.datapoint import ValueMessageByDatapointId
from esg.models.datapoint import ValueMessageListByDatapointId
from esg.models.datapoint import ScheduleMessageByDatapointId
from esg.models.datapoint import ScheduleMessageListByDatapointId
from esg.models.datapoint import SetpointMessageByDatapointId
from esg.models.datapoint import SetpointMessageListByDatapointId
from esg.models.datapoint import ForecastMessageListByDatapointId
from esg.models.metadata import ProductList
from esg.models.metadata import ProductRunList
from esg.models.metadata import PlantList
from esg.models.request import HTTPError
from esg.services.base import RequestInducedException

from .models import Datapoint as DatapointDb
from emp_main.models import ValueMessage as ValueHistoryDb
from emp_main.models import LastValueMessage as ValueLatestDb
from emp_main.models import ScheduleMessage as ScheduleHistoryDb
from emp_main.models import LastScheduleMessage as ScheduleLatestDb
from emp_main.models import SetpointMessage as SetpointHistoryDb
from emp_main.models import LastSetpointMessage as SetpointLatestDb
from emp_main.models import ForecastMessage as ForecastMessageDb
from emp_main.models import Product as ProductDb
from emp_main.models import ProductRun as ProductRunDb
from emp_main.models import Plant as PlantDb

logger = logging.getLogger(__name__)


api = NinjaAPI(title="EMP API", version="v1", docs_url="/",)


class GenericAPIView:
    """
    Some generic stuff that should be relevant for all API endpoints.

    Attributes:
    -----------
    PydanticModel: esg.models._BaseModel instance
        The Model that should be used to parse the input of `update_*` and
        serialize the output of `list_*` operations.
    DBModel: esg.django_models.DjangoBaseModel instance.
        The django model to interact with the DB.
    """

    PydanticModel = None
    DBModel = None

    unique_together_fields_latest = ["id"]

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
            except Http404 as exception:
                http_error = HTTPError(detail=str(exception))
                return HttpResponse(
                    http_error.json(),
                    status=404,
                    content_type="application/json",
                )
                raise
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

    def build_active_filter_dict(self, filter_params=None):
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
        if filter_params is not None:
            for filter_key, filter_value in filter_params:
                if filter_value is None:
                    continue
                active_filters[filter_key] = filter_value
        return active_filters

    @_handle_exceptions
    def list_latest(self, request, filter_params=None):
        """
        List latest state of plants.

        This works only for models that inherit from
        `esg.django_models.base.DjangoBaseModel`
        """
        objects_all = self.DBModel.objects.all()

        active_filters = self.build_active_filter_dict(filter_params)
        objects_filtered = objects_all.filter(**active_filters)

        objects_as_python = []
        for object in objects_filtered:
            objects_as_python.append(object.load_to_dict())

        objects_pydantic = self.PydanticModel.construct_recursive(
            __root__=objects_as_python
        )

        objects_json = objects_pydantic.json()

        return HttpResponse(
            content=objects_json, status=200, content_type="application/json"
        )

    @_handle_exceptions
    def update_latest(self, request, objects_pydantic):
        """
        Update or create the latest state of the data items.

        Arguments:
        ----------
        objects_pydantic: A pydantic model instance.
            This method expects a model with a list as root element and
            list items which correspond each to one object in `self.DbModel`.
        """
        # Statistics for the return value.
        objects_created = 0
        objects_updated = 0

        # Fetch objects that are updated and create new ones.
        objects_db_pydantic = []
        for object_pydantic in objects_pydantic.__root__:

            unique_field_values = {}
            for field_name in self.unique_together_fields_latest:
                field_value = getattr(object_pydantic, field_name)
                unique_field_values[field_name] = field_value

            try:
                object_db = self.DBModel.objects.get(**unique_field_values)
                objects_updated += 1
            except self.DBModel.DoesNotExist:
                object_db = self.DBModel(**unique_field_values)
                objects_created += 1

            objects_db_pydantic.append((object_db, object_pydantic))

        try:
            with transaction.atomic():
                for object_db, object_pydantic in objects_db_pydantic:
                    object_db.save_from_pydantic(object_pydantic)
        except IntegrityError as exp:
            raise RequestInducedException(
                detail=(
                    'Exception while writing messae `{}` to DB: "{}".'
                    "".format(object_pydantic.json(), str(exp))
                )
            )

        # Finally report, the stats
        content_pydantic = PutSummary(
            objects_created=objects_created, objects_updated=objects_updated,
        )
        content = content_pydantic.json()

        return HttpResponse(
            content, status=200, content_type="application/json"
        )


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

    def __init__(self):
        """
        Define the channel layer for pushing stuff to websockets.
        """
        self.channel_layer = get_channel_layer()

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

    def get_datapoints_by_ids(self, datapoint_ids_as_str):
        """
        Fetches datapoint objects given a list of IDs.

        Arguments:
        ----------
        datapoint_ids_as_str: list of str.
            This is a list of IDs as str because OpenAPI models use
            strs as dict keys and we need to check some edge cases here,
            like that the ID is not an int.

        Returns:
        --------
        datapoints_db_by_id = dict {str : datapoint object}
            The found datapoint object for the IDs.

        Raises:
        -------
        RequestInducedException:
            If datapoints could not be found for one or more IDs
        """
        datapoint_ids = []
        for id in datapoint_ids_as_str:
            try:
                datapoint_ids.append(int(id))
            except ValueError:
                # Ignore any ID that can't be converted to ID, it can't
                # be in DB anyways and the check below should raise an
                # appropriate error.
                pass

        datapoints_db = self.DatapointModel.objects.filter(id__in=datapoint_ids)

        datapoints_db_by_id = {}
        for datapoint_db in datapoints_db:
            datapoints_db_by_id[str(datapoint_db.id)] = datapoint_db

        # Check if some datapoints are not available in DB.
        # Note that we must compare strings here, to also raise
        # errors for IDs that have failed conversion to int above.
        expected_dp_ids = set([id for id in datapoint_ids_as_str])
        actual_dp_ids = set([id for id in datapoints_db_by_id.keys()])
        if expected_dp_ids != actual_dp_ids:
            raise RequestInducedException(
                detail=(
                    "The following datapoint ids do not exist: {}"
                    "".format(list(expected_dp_ids - actual_dp_ids))
                )
            )

        return datapoints_db_by_id


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
    RelatedDataHistoryModel : django.db.models.Model
        A second model that is related apart from Datapoint.
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
    unique_together_fields_latest: list of str
        A list of field names that identify a unqiue message in the latest
        table. This is used to check if an entry is updated or created.
    unique_together_fields_history: list of str
        Like `unique_together_fields_latest` but for `RelatedDataHistoryModel`.
    second_related_field_name : str
        The field name of the second related field.
    channel_group_base_name: str
        The the non datapoint id dependend part of the channels group name.

    """

    RelatedDataLatestModel = None
    RelatedDataHistoryModel = None
    SecondRelatedModel = None
    list_latest_response_model = None
    list_history_response_model = None
    update_latest_response_model = None
    unique_together_fields_latest = ["datapoint"]
    unique_together_fields_history = ["datapoint", "time"]
    second_related_field_name = None
    channel_group_base_name = None

    @GenericAPIView._handle_exceptions
    def list_latest(
        self,
        request,
        datapoint_filter_params,
        related_filter_params,
        second_related_filter_params=None,
    ):
        """
        Returns the latest data item per datapoint.
        """
        # TODO: Add test that list calls this method to fetch filtered
        #       datapoints, and of course that the query params are forewarded.
        datapoints = self.get_filtered_datapoints(datapoint_filter_params)

        related_objects = self.RelatedDataLatestModel.objects.filter(
            datapoint__in=datapoints
        )

        # Filter by query parameters.
        # NOTE: If this filter is applied or not is not covered in the test.
        #       If you change someting in this block be extra careful and test
        #       manually afterwards.
        # TODO: Add tests that filter is applied.
        active_filters = self.build_active_filter_dict(related_filter_params)
        if self.SecondRelatedModel is not None:
            # Add some additional filter if a second related object is defined.
            active_filters_second = self.build_active_filter_dict(
                second_related_filter_params
            )
            active_filters.update(active_filters_second)
        related_objects = related_objects.filter(**active_filters)

        # Group by datapoint ID.
        related_objects_as_dict = {}
        for obj in related_objects:
            related_objects_as_dict[str(obj.datapoint.id)] = obj.load_to_dict()

        # Convert to jsonable, skip validation.
        output_pydantic_model = self.list_latest_response_model
        related_objects_as_pydantic = output_pydantic_model.construct_recursive(
            __root__=related_objects_as_dict
        )

        related_objects_as_json = related_objects_as_pydantic.json()

        return HttpResponse(
            content=related_objects_as_json,
            status=200,
            content_type="application/json",
        )

    @GenericAPIView._handle_exceptions
    def list_history(
        self,
        request,
        datapoint_filter_params,
        related_filter_params,
        second_related_filter_params=None,
    ):
        """
        Returns the historic data item per datapoint.
        """
        datapoints = self.get_filtered_datapoints(datapoint_filter_params)

        related_objects = self.RelatedDataHistoryModel.objects.filter(
            datapoint__in=datapoints
        )

        # Filter by query parameters.
        # NOTE: If this filter is applied or not is not covered in the test.
        #       If you change something in this block be extra careful and test
        #       manually afterwards.
        # TODO: Add tests that filter is applied.
        active_filters = self.build_active_filter_dict(related_filter_params)
        if self.SecondRelatedModel is not None:
            # Add some additional filter if a second related object is defined.
            active_filters_second = self.build_active_filter_dict(
                second_related_filter_params
            )
            active_filters.update(active_filters_second)
        related_objects = related_objects.filter(**active_filters)

        # Make a list of objects belonging to datapoint ID for each datapoint.
        related_objects_as_dict = {}
        for obj in related_objects:
            dp_id = str(obj.datapoint.id)
            objects_datapoint = related_objects_as_dict.get(dp_id, [])
            objects_datapoint.append(obj.load_to_dict())
            related_objects_as_dict[dp_id] = objects_datapoint

        # Convert to jsonable, skip validation.
        output_pydantic_model = self.list_history_response_model
        related_objects_as_pydantic = output_pydantic_model.construct_recursive(
            __root__=related_objects_as_dict
        )

        related_objects_as_json = related_objects_as_pydantic.json()

        return HttpResponse(
            content=related_objects_as_json,
            status=200,
            content_type="application/json",
        )

    @GenericAPIView._handle_exceptions
    def update_latest(
        self, request, related_data, second_related_filter_params=None
    ):
        """
        Update or create the latest state of the data items.
        """

        if self.SecondRelatedModel is not None:
            active_filters_second = self.build_active_filter_dict(
                second_related_filter_params
            )
            second_related_object = get_object_or_404(
                self.SecondRelatedModel, **active_filters_second
            )

        related_data_dict = related_data.dict()["__root__"]

        # Fetch the datapoint objects belonging to the data.
        datapoints_db_by_id = self.get_datapoints_by_ids(
            datapoint_ids_as_str=related_data_dict.keys()
        )

        # Now we have passed all validation (the validation of the input
        # model, the validation that all datapoints exist and maybe
        # the check that the second related model exists) we can savely
        # create the content for the channels layer.
        # NOTE: This must be done before we modify the related data items
        # below.
        related_data_json_by_id = {}
        for dp_id in related_data_dict:
            single_dp_dict = {dp_id: related_data_dict[dp_id]}
            pydantic_model = self.list_latest_response_model
            single_dp_pydantic = pydantic_model.construct_recursive(
                __root__=single_dp_dict
            )
            single_dp_json = single_dp_pydantic.json()
            related_data_json_by_id[dp_id] = single_dp_json

        # Flatten to prepare for bulk update.
        # TODO: This is actually stupid, we flatten here and bulk_update
        # sorts back by datapoint id.
        related_data_items = []
        for datapoint_id_str, related_data_item in related_data_dict.items():
            related_data_item["datapoint"] = datapoints_db_by_id[
                datapoint_id_str
            ]
            if self.SecondRelatedModel is not None:
                field_name = self.second_related_field_name
                related_data_item[field_name] = second_related_object
            related_data_items.append(related_data_item)

        # Write into latest table.
        summary = self.RelatedDataLatestModel.bulk_update_or_create(
            self.RelatedDataLatestModel, related_data_items
        )

        # Also write into history table.
        _ = self.RelatedDataHistoryModel.bulk_update_or_create(
            self.RelatedDataHistoryModel, related_data_items
        )

        # Publish updated data on channel layer.
        # TODO: Make this parallel
        for dp_id, single_dp_json in related_data_json_by_id.items():
            async_to_sync(self.channel_layer.group_send)(
                self.channel_group_base_name + dp_id,
                {"type": "datapoint.related", "json": single_dp_json},
            )

        # Finally report, the stats
        content_pydantic = PutSummary(
            objects_created=summary[0], objects_updated=summary[1],
        )
        content = content_pydantic.json()

        return HttpResponse(
            content, status=200, content_type="application/json"
        )

    @GenericAPIView._handle_exceptions
    def update_history(
        self, request, related_data, second_related_filter_params=None,
    ):
        """
        Update or create the latest state of the data items.
        """
        if self.SecondRelatedModel is not None:
            active_filters_second = self.build_active_filter_dict(
                second_related_filter_params
            )
            second_related_object = get_object_or_404(
                self.SecondRelatedModel, **active_filters_second
            )

        related_data_dict = related_data.dict()["__root__"]

        # Fetch the datapoint objects belonging to the data.
        datapoints_db_by_id = self.get_datapoints_by_ids(
            datapoint_ids_as_str=related_data_dict.keys()
        )

        # Flatten to prepare for bulk update.
        # TODO: This is actually stupid, we flatten here and bulk_update
        # sorts back by datapoint id.
        related_data_items = []
        for datapoint_id_str, related_data_list in related_data_dict.items():
            for related_data_item in related_data_list:
                related_data_item["datapoint"] = datapoints_db_by_id[
                    datapoint_id_str
                ]
                if self.SecondRelatedModel is not None:
                    field_name = self.second_related_field_name
                    related_data_item[field_name] = second_related_object
                related_data_items.append(related_data_item)

        summary = self.RelatedDataHistoryModel.bulk_update_or_create(
            self.RelatedDataHistoryModel, related_data_items
        )

        # Finally report, the stats
        content_pydantic = PutSummary(
            objects_created=summary[0], objects_updated=summary[1],
        )
        content = content_pydantic.json()

        return HttpResponse(
            content, status=200, content_type="application/json"
        )


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
        for dp_id in created_datapoints_pydantic.__root__:
            dp_pydantic = created_datapoints_pydantic.__root__[dp_id]
            dp_json = dp_pydantic.json()
            async_to_sync(self.channel_layer.group_send)(
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


##############################################################################
# Datapoint Value Messages -> /datapoint/value/*
##############################################################################


class DatapointValueAPIView(GenericDatapointRelatedAPIView):
    RelatedDataLatestModel = ValueLatestDb
    RelatedDataHistoryModel = ValueHistoryDb
    list_latest_response_model = ValueMessageByDatapointId
    list_history_response_model = ValueMessageListByDatapointId
    update_latest_websocket_model = ValueMessageByDatapointId
    channel_group_base_name = "datapoint.value.latest."

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


@api.put(
    "/datapoint/value/latest/",
    response={200: PutSummary, 400: HTTPError, 500: HTTPError},
    tags=["Datapoint Value"],
    summary=" ",  # Deactivate summary.
)
def put_datapoint_value_latest(
    request, value_messages_by_datapoint_id: ValueMessageByDatapointId,
):
    """
    Update or create the latest value messages for one or more datapoints.
    """

    response = dp_value_view.update_latest(
        request=request, related_data=value_messages_by_datapoint_id,
    )
    return response


@api.put(
    "/datapoint/value/history/",
    response={200: PutSummary, 400: HTTPError, 500: HTTPError},
    tags=["Datapoint Value"],
    summary=" ",  # Deactivate summary.
)
def put_datapoint_value_history(
    request, value_messages_by_datapoint_id: ValueMessageListByDatapointId,
):
    """
    Update or create one or more historic value messages for each of one
    or more datapoints.
    """

    response = dp_value_view.update_history(
        request=request, related_data=value_messages_by_datapoint_id,
    )
    return response


##############################################################################
# Datapoint Schedule Messages -> /datapoint/schedule/*
##############################################################################


class DatapointScheduleAPIView(GenericDatapointRelatedAPIView):
    RelatedDataLatestModel = ScheduleLatestDb
    RelatedDataHistoryModel = ScheduleHistoryDb
    list_latest_response_model = ScheduleMessageByDatapointId
    list_history_response_model = ScheduleMessageListByDatapointId
    update_latest_websocket_model = ScheduleMessageByDatapointId
    channel_group_base_name = "datapoint.schedule.latest."

    # This is defined here every time to adapt the field descriptions.
    # TODO: Add test that these filters are applicable to the target model.
    class ScheduleFilterParams(Schema):
        time__gte: datetime = Field(
            None,
            description="`ScheduleMessage.time` greater or equal this value.",
        )
        time__lt: datetime = Field(
            None, description="`ScheduleMessage.time` less this value."
        )


dp_schedule_view = DatapointScheduleAPIView()


@api.get(
    "/datapoint/schedule/latest/",
    response={
        200: ScheduleMessageByDatapointId,
        400: HTTPError,
        500: HTTPError,
    },
    tags=["Datapoint Schedule"],
    summary=" ",  # Deactivate summary.
)
def get_datapoint_schedule_latest(
    request,
    datapoint_filter_params: dp_schedule_view.DatapointFilterParams = Query(
        ...
    ),
    schedule_filter_params: dp_schedule_view.ScheduleFilterParams = Query(...),
):
    """
    Return the latest schedules for datapoints targeted by the filter.
    """

    response = dp_schedule_view.list_latest(
        request=request,
        datapoint_filter_params=datapoint_filter_params,
        related_filter_params=schedule_filter_params,
    )
    return response


@api.get(
    "/datapoint/schedule/history/",
    response={
        200: ScheduleMessageListByDatapointId,
        400: HTTPError,
        500: HTTPError,
    },
    tags=["Datapoint Schedule"],
    summary=" ",  # Deactivate summary.
)
def get_datapoint_schedule_history(
    request,
    datapoint_filter_params: dp_schedule_view.DatapointFilterParams = Query(
        ...
    ),
    schedule_filter_params: dp_schedule_view.ScheduleFilterParams = Query(...),
):
    """
    Return one or more schedule messages for datapoints targeted by the filter.
    """

    response = dp_schedule_view.list_history(
        request=request,
        datapoint_filter_params=datapoint_filter_params,
        related_filter_params=schedule_filter_params,
    )
    return response


@api.put(
    "/datapoint/schedule/latest/",
    response={200: PutSummary, 400: HTTPError, 500: HTTPError},
    tags=["Datapoint Schedule"],
    summary=" ",  # Deactivate summary.
)
def put_datapoint_schedule_latest(
    request, schedule_messages_by_datapoint_id: ScheduleMessageByDatapointId,
):
    """
    Return the historic schedule for datapoints targeted by the filter.
    """

    response = dp_schedule_view.update_latest(
        request=request, related_data=schedule_messages_by_datapoint_id,
    )
    return response


@api.put(
    "/datapoint/schedule/history/",
    response={200: PutSummary, 400: HTTPError, 500: HTTPError},
    tags=["Datapoint Schedule"],
    summary=" ",  # Deactivate summary.
)
def put_datapoint_schedule_history(
    request,
    schedule_messages_by_datapoint_id: ScheduleMessageListByDatapointId,
):
    """
    Return the latest schedules for datapoints targeted by the filter.
    """

    response = dp_schedule_view.update_history(
        request=request, related_data=schedule_messages_by_datapoint_id,
    )
    return response


##############################################################################
# Datapoint Setpoint Messages -> /datapoint/setpoint/*
##############################################################################


class DatapointSetpointAPIView(GenericDatapointRelatedAPIView):
    RelatedDataLatestModel = SetpointLatestDb
    RelatedDataHistoryModel = SetpointHistoryDb
    list_latest_response_model = SetpointMessageByDatapointId
    list_history_response_model = SetpointMessageListByDatapointId
    update_latest_websocket_model = SetpointMessageByDatapointId
    channel_group_base_name = "datapoint.setpoint.latest."

    # This is defined here every time to adapt the field descriptions.
    # TODO: Add test that these filters are applicable to the target model.
    class SetpointFilterParams(Schema):
        time__gte: datetime = Field(
            None,
            description="`SetpointMessage.time` greater or equal this value.",
        )
        time__lt: datetime = Field(
            None, description="`SetpointMessage.time` less this value."
        )


dp_setpoint_view = DatapointSetpointAPIView()


@api.get(
    "/datapoint/setpoint/latest/",
    response={
        200: SetpointMessageByDatapointId,
        400: HTTPError,
        500: HTTPError,
    },
    tags=["Datapoint Setpoint"],
    summary=" ",  # Deactivate summary.
)
def get_datapoint_setpoint_latest(
    request,
    datapoint_filter_params: dp_setpoint_view.DatapointFilterParams = Query(
        ...
    ),
    setpoint_filter_params: dp_setpoint_view.SetpointFilterParams = Query(...),
):
    """
    Return the latest setpoints for datapoints targeted by the filter.
    """

    response = dp_setpoint_view.list_latest(
        request=request,
        datapoint_filter_params=datapoint_filter_params,
        related_filter_params=setpoint_filter_params,
    )
    return response


@api.get(
    "/datapoint/setpoint/history/",
    response={
        200: SetpointMessageListByDatapointId,
        400: HTTPError,
        500: HTTPError,
    },
    tags=["Datapoint Setpoint"],
    summary=" ",  # Deactivate summary.
)
def get_datapoint_setpoint_history(
    request,
    datapoint_filter_params: dp_setpoint_view.DatapointFilterParams = Query(
        ...
    ),
    setpoint_filter_params: dp_setpoint_view.SetpointFilterParams = Query(...),
):
    """
    Return one or more setpoint messages for datapoints targeted by the filter.
    """

    response = dp_setpoint_view.list_history(
        request=request,
        datapoint_filter_params=datapoint_filter_params,
        related_filter_params=setpoint_filter_params,
    )
    return response


@api.put(
    "/datapoint/setpoint/latest/",
    response={200: PutSummary, 400: HTTPError, 500: HTTPError},
    tags=["Datapoint Setpoint"],
    summary=" ",  # Deactivate summary.
)
def put_datapoint_setpoint_latest(
    request, setpoint_messages_by_datapoint_id: SetpointMessageByDatapointId,
):
    """
    Return the historic setpoint for datapoints targeted by the filter.
    """

    response = dp_setpoint_view.update_latest(
        request=request, related_data=setpoint_messages_by_datapoint_id,
    )
    return response


@api.put(
    "/datapoint/setpoint/history/",
    response={200: PutSummary, 400: HTTPError, 500: HTTPError},
    tags=["Datapoint Setpoint"],
    summary=" ",  # Deactivate summary.
)
def put_datapoint_setpoint_history(
    request,
    setpoint_messages_by_datapoint_id: SetpointMessageListByDatapointId,
):
    """
    Return the latest setpoints for datapoints targeted by the filter.
    """

    response = dp_setpoint_view.update_history(
        request=request, related_data=setpoint_messages_by_datapoint_id,
    )
    return response


##############################################################################
# Datapoint Forecast Messages -> /datapoint/forecasts/*
##############################################################################


class DatapointForecastAPIView(GenericDatapointRelatedAPIView):
    """
    NOTE: Actually, this model only provides a latest endpoint as we currently
          only track the latest version of the results of a product run (and
          not changes from updates for a product run). However, we nevertheless
          use the history endpoints of `GenericDatapointRelatedAPIView` as
          this one can handle list of items per datapoint, which is the case
          here. This is fine as long we are not interested in pushing
          updates via websocket.
    """

    RelatedDataHistoryModel = ForecastMessageDb
    list_history_response_model = ForecastMessageListByDatapointId
    SecondRelatedModel = ProductRunDb
    second_related_field_name = "product_run"

    class ForecastFilterParams(Schema):
        time__gte: datetime = Field(
            None,
            description="`ForecastMessage.time` greater or equal this value.",
        )
        time__lt: datetime = Field(
            None, description="`ForecastMessage.time` less this value."
        )

    class PathParams(Schema):
        id: int = Field(
            ...,
            description=(
                "`ProductRun.id` to which the forecast messages belong to."
            ),
        )


dp_forecast_view = DatapointForecastAPIView()


@api.get(
    "/datapoint/forecast/latest/{id}/",
    response={
        200: ForecastMessageListByDatapointId,
        400: HTTPError,
        404: HTTPError,
        500: HTTPError,
    },
    tags=["Datapoint Forecast"],
    summary=" ",  # Deactivate summary.
)
def get_datapoint_forecast_latest(
    request,
    product_run_filter_params: dp_forecast_view.PathParams = Path(...),
    datapoint_filter_params: dp_forecast_view.DatapointFilterParams = Query(
        ...
    ),
    forecast_filter_params: dp_forecast_view.ForecastFilterParams = Query(...),
):
    """
    Return the latest setpoints for datapoints targeted by the filter.
    """

    response = dp_forecast_view.list_history(
        request=request,
        datapoint_filter_params=datapoint_filter_params,
        related_filter_params=forecast_filter_params,
        second_related_filter_params=product_run_filter_params,
    )
    return response


@api.put(
    "/datapoint/forecast/latest/{id}/",
    response={200: PutSummary, 400: HTTPError, 404: HTTPError, 500: HTTPError},
    tags=["Datapoint Forecast"],
    summary=" ",  # Deactivate summary.
)
def put_datapoint_forecast_latest(
    request,
    forecast_messages_by_datapoint_id: ForecastMessageListByDatapointId,
    product_run_filter_params: dp_forecast_view.PathParams = Path(...),
):
    """
    Return the historic setpoint for datapoints targeted by the filter.
    """

    response = dp_forecast_view.update_history(
        request=request,
        related_data=forecast_messages_by_datapoint_id,
        second_related_filter_params=product_run_filter_params,
    )
    return response


##############################################################################
# Product Messages -> /product/*
##############################################################################


class ProductAPIView(GenericAPIView):
    PydanticModel = ProductList
    DBModel = ProductDb


product_view = ProductAPIView()


@api.get(
    "/product/latest/",
    response={200: ProductList, 400: HTTPError, 500: HTTPError},
    tags=["Product"],
    summary=" ",  # Deactivate summary.
)
def get_product_latest(request):
    """
    Return the latest state of the `Product` objects.

    Each entry specifies the metadata necessary (alongside with `Plant`) to
    trigger requests to a defined product service, like e.g. a PV Forecast.
    """

    response = product_view.list_latest(request=request)
    return response


@api.put(
    "/product/latest/",
    response={200: PutSummary, 400: HTTPError, 500: HTTPError},
    tags=["Product"],
    summary=" ",  # Deactivate summary.
)
def put_product_latest(request, objects_pydantic: ProductList):
    """
    Update the latest state of one or more `Product` objects.

    Each entry specifies the metadata necessary (alongside with `Plant`) to
    trigger requests to a defined product service, like e.g. a PV Forecast.
    """

    response = product_view.update_latest(
        request=request, objects_pydantic=objects_pydantic
    )
    return response


##############################################################################
# Product Run Messages -> /product_run/*
##############################################################################


class ProductRunAPIView(GenericAPIView):
    PydanticModel = ProductRunList
    DBModel = ProductRunDb


product_run_view = ProductRunAPIView()


@api.get(
    "/product_run/latest/",
    response={200: ProductRunList, 400: HTTPError, 500: HTTPError},
    tags=["Product Run"],
    summary=" ",  # Deactivate summary.
)
def get_product_run_latest(request):
    """
    Return the latest state of the `Product` objects.

    Each entry specifies the metadata necessary (alongside with `Plant`) to
    trigger requests to a defined product service, like e.g. a PV Forecast.
    """

    response = product_run_view.list_latest(request=request)
    return response


@api.put(
    "/product_run/latest/",
    response={200: PutSummary, 400: HTTPError, 500: HTTPError},
    tags=["Product Run"],
    summary=" ",  # Deactivate summary.
)
def put_product_run_latest(request, objects_pydantic: ProductRunList):
    """
    Update the latest state of one or more `Product` objects.

    Each entry specifies the metadata necessary (alongside with `Plant`) to
    trigger requests to a defined product service, like e.g. a PV Forecast.
    """

    response = product_run_view.update_latest(
        request=request, objects_pydantic=objects_pydantic
    )
    return response


##############################################################################
# Plant Messages -> /plant/*
##############################################################################


class PlantAPIView(GenericAPIView):
    PydanticModel = PlantList
    DBModel = PlantDb

    class PlantFilterParams(Schema):
        product__id__in: str = Field(
            None,
            description=("Matches `Plant` with `product_ids` in this list."),
        )


plant_view = PlantAPIView()


@api.get(
    "/plant/latest/",
    response={200: PlantList, 400: HTTPError, 500: HTTPError},
    tags=["Plant"],
    summary=" ",  # Deactivate summary.
)
def get_plant_latest(
    request, filter_params: plant_view.PlantFilterParams = Query(...),
):
    """
    Return the latest state of the Plant objects.

    Plants define the metadata necessary to compute optimized schedules or
    forecasts for a physical entities, e.g. represent PV plants or buildings.
    """

    response = plant_view.list_latest(
        request=request, filter_params=filter_params
    )
    return response


@api.put(
    "/plant/latest/",
    response={200: PutSummary, 400: HTTPError, 500: HTTPError},
    tags=["Plant"],
    summary=" ",  # Deactivate summary.
)
def put_plant_latest(request, objects_pydantic: PlantList):
    """
    Update the latest state of one or more `Product` objects.

    Each entry specifies the metadata necessary (alongside with `Plant`) to
    trigger requests to a defined product service, like e.g. a PV Forecast.
    """

    response = plant_view.update_latest(
        request=request, objects_pydantic=objects_pydantic
    )
    return response
