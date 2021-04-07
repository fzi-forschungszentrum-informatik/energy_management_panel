from rest_framework import serializers

from emp_main.models import Datapoint


class DatapointSerializer(serializers.ModelSerializer):
    """
    A Copy of the serializer from ems_utils but with the correct Datapoint
    model associated to it.
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
