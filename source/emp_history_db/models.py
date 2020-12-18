from django.db import models

from emp_main.models import Datapoint


class DatapointValue(models.Model):

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=(
            "The datapoint that the value message belongs to."
        )
    )
    value = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The value field in datapoint value msg."
        )
    )
    timestamp = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The field that stores the timestamp of value msg as datetime."
        )
    )
