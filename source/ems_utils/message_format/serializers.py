from datetime import datetime

from rest_framework import serializers

from emp_main.models import Datapoint


class DatapointSerializer(serializers.HyperlinkedModelSerializer):
    """
    Metadata of a datapoint.
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
            ]
        read_only_fields = [
            "id",
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
    Value message for a datapoint.

    The value measured by sensor datapoint, or the set value send to an
    actuator.

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
    """
    Represents the optimized actuator value for one interval in time.
    """
    from_timestamp = serializers.IntegerField(
        allow_null=True,
        help_text=(
            "The time in milliseconds since 1970-01-01 UTC that the value "
            "should be applied. Can be `null` in which case the value should "
            "be applied immediately after the schedule is received."
        )
    )
    to_timestamp = serializers.IntegerField(
        allow_null=True
    )
    value = serializers.CharField(
        allow_null=True
    )

class DatapointScheduleSerializer(serializers.Serializer):
    """
    The schedule is list of actuator values computed by an optimization
    algorithm that should be executed on the specified actuator datapoint
    if the setpoint is not violated.

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
    """
    The user requested value for a one time interval.
    """
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
    Represents the demand that a user specifies for a datapoint, i.e. the
    range of values (or single value) the user is willing to except.

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
