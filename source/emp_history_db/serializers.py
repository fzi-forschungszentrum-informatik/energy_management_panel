from datetime import datetime

from rest_framework import serializers

from .apps import app_url_prefix
from emp_main.models import Datapoint


class DatapointSerializer(serializers.HyperlinkedModelSerializer):
    """
    Show metadata for one/many datapoints.

    TODO: Specify allwed_values as list of strings.
    """
    class Meta:
        model = Datapoint
        fields = [
            "id",
            "origin_id",
            "type",
            "data_format",
            "short_name",
            "description",
            "origin_description",
            "min_value",
            "max_value",
            "allowed_values",
            "unit",
            "last_value",
            "last_value_timestamp",
            "last_setpoint",
            "last_setpoint_timestamp",
            "last_schedule",
            "last_schedule_timestamp",
            ]
        read_only_fields = [
            "id",
            "short_name",
            "description",
            "last_value",
            "last_value_timestamp",
            "last_setpoint",
            "last_setpoint_timestamp",
            "last_schedule",
            "last_schedule_timestamp",
        ]
        # Disable the unqieness check for datapoint. We just update
        # for simplicity.
        extra_kwargs = {
            'origin_id': {
                'validators': [],
            }
        }


class DatapointValueSerializer(serializers.Serializer):
    """
    TODO: Extend validation here.
    """
    value = serializers.CharField(
        allow_null=True
    )
    timestamp = serializers.IntegerField(
        allow_null=False
    )

    def to_representation(self, instance):
        fields_values = {}
        fields_values["value"] = instance.value
        # Return datetime in ms.
        if instance.timestamp is not None:
            timestamp = datetime.timestamp(instance.timestamp)
            timestamp_ms = round(timestamp * 1000)
            fields_values["timestamp"] = timestamp_ms
        else:
            fields_values["timestamp"] = None
        return fields_values


class DatapointScheduleItemSerializer(serializers.Serializer):
    from_timestamp = serializers.IntegerField(
        allow_null=True
    )
    to_timestamp = serializers.IntegerField(
        allow_null=True
    )
    value = serializers.CharField(
        allow_null=True
    )

class DatapointScheduleSerializer(serializers.Serializer):
    """
    TODO: Extend validation here.
    """
    schedule = DatapointScheduleItemSerializer(
        many=True,
        read_only=False
    )
    timestamp = serializers.IntegerField(
        allow_null=False
    )

    def to_representation(self, instance):
        fields_values = {}
        fields_values["schedule"] = instance.schedule
        # Return datetime in ms.
        if instance.timestamp is not None:
            timestamp = datetime.timestamp(instance.timestamp)
            timestamp_ms = round(timestamp * 1000)
            fields_values["timestamp"] = timestamp_ms
        else:
            fields_values["timestamp"] = None
        return fields_values

class DatapointSetpointItemSerializer(serializers.Serializer):
    from_timestamp = serializers.IntegerField(
        allow_null=True,
    )
    to_timestamp = serializers.IntegerField(
        allow_null=True,
    )
    preferred_value = serializers.CharField(
        allow_null=True,
    )
    acceptable_values = serializers.ListField(
        child=serializers.CharField(
            allow_null=False
        ),
        allow_null=True,
        required=False,
    )
    min_value = serializers.FloatField(
        allow_null=True,
        required=False,
    )
    max_value = serializers.FloatField(
        allow_null=True,
        required=False,
    )


class DatapointSetpointSerializer(serializers.Serializer):
    """
    TODO: Extend validation here.
    """
    setpoint = DatapointSetpointItemSerializer(
        many=True,
        read_only=False
    )
    timestamp = serializers.IntegerField(
        allow_null=False
    )

    def to_representation(self, instance):
        fields_values = {}
        fields_values["setpoint"] = instance.setpoint
        # Return datetime in ms.
        if instance.timestamp is not None:
            timestamp = datetime.timestamp(instance.timestamp)
            timestamp_ms = round(timestamp * 1000)
            fields_values["timestamp"] = timestamp_ms
        else:
            fields_values["timestamp"] = None
        return fields_values
