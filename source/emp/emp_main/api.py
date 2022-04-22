#!/usr/bin/env python3
"""
Definition of EMP REST API.

This API is all syncronous as the Django ORM and Middlewares are not async yet.
Django recommends to limit switching from async to sync, and as the ASGI is
used for access with keep it sync afterwards. See:
https://docs.djangoproject.com/en/3.2/topics/async/
"""
import json
from typing import List

from django.forms.models import model_to_dict
from django.http import HttpResponse
from ninja import NinjaAPI
from ninja import Query
from ninja import Schema
from ninja.renderers import BaseRenderer

from .models import Datapoint as DatapointDb
from esg.models.datapoint import DatapointById
from esg.models.datapoint import DatapointType
from esg.models.datapoint import DatapointDataFormat


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

    def list(self, request, datapoint_filter_params={}):
        """
        Return a queryset of datapoints matching the requested filter
        parameters.

        Arguments:
        ----------
        datapoint_filter_params: instance of `DatapointFilterParams`
            Defines the filters that should be applied to the datapoints.
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


class DatapointView(GenericDatapointRelatedView):
    pass


dp_view = DatapointView()


class Test:
    @api.get(
        "/datapoint/", response={200: DatapointById},
    )
    def get_test(
        request,
        datapoint_filter_params: dp_view.DatapointFilterParams = Query(...),
    ):
        response = dp_view.list(
            request=request, datapoint_filter_params=datapoint_filter_params
        )
        return response
