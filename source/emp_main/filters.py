from django_filters import FilterSet, NumberFilter

from emp_main.models import Datapoint
from emp_main.models import DatapointValue
from emp_main.models import DatapointSchedule
from emp_main.models import DatapointSetpoint
from ems_utils.timestamp import datetime_from_timestamp


class DatapointFilter(FilterSet):
    """
    Some useful filters for the Datapoint list.
    """
    class Meta:
        model = Datapoint
        fields = {
            "short_name": ["exact", "icontains"],
            "type": ["exact"],
            "data_format": ["exact", "icontains"],
            "unit": ["exact", "icontains"],
            "origin_id": ["exact", "icontains"],
        }


class TimestampFilter(FilterSet):
    timestamp__gte = NumberFilter(
        field_name="timestamp__gte",
        lookup_expr="gte",
        method="filter_timestamp",
    )
    timestamp__gt = NumberFilter(
        field_name="timestamp__gt",
        lookup_expr="gt",
        method="filter_timestamp",
    )
    timestamp__lte = NumberFilter(
        field_name="timestamp__lte",
        lookup_expr="lte",
        method="filter_timestamp",
    )
    timestamp__lt = NumberFilter(
        field_name="timestamp__lt",
        lookup_expr="lt",
        method="filter_timestamp",
    )

    def filter_timestamp(self, queryset, lookup_expr, value):
        lookup = "__".join([lookup_expr])
        ts_as_dt = datetime_from_timestamp(float(value))
        return queryset.filter(**{lookup: ts_as_dt})


class DatapointValueFilter(TimestampFilter):
    """
    Allows selecting values by timestamp ranges.
    """

    class Meta:
        model = DatapointValue
        fields = [] # The custom methods are added automatically.

class DatapointSetpointFilter(TimestampFilter):
    """
    Allows selecting values by timestamp ranges.
    """
    class Meta:
        model = DatapointSetpoint
        fields = [] # The custom methods are added automatically.


class DatapointScheduleFilter(TimestampFilter):
    """
    Allows selecting values by timestamp ranges.
    """
    class Meta:
        model = DatapointSchedule
        fields = [] # The custom methods are added automatically.
