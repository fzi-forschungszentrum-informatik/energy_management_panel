import json

from django.db import models
from django.core.exceptions import ValidationError

from ems_utils.message_format.models import DatapointTemplate
from ems_utils.message_format.models import DatapointValueTemplate
from ems_utils.message_format.models import DatapointSetpointTemplate
from ems_utils.message_format.models import DatapointScheduleTemplate


class ModelWithIterableFields(models.Model):
    """
    A model that supports iterating over fields.

    This is usefull if you want to display a model with all fields/values on
    a page, e.g. as a table.
    """

    class Meta:
        abstract = True

    def iter_fields(self):
        """
        Return fields and values to display in the device detail modal.
        """
        fields = self._meta.fields
        field_names = []
        field_values = []
        for field in fields:
            field_names.append(field.name)
            field_values.append(getattr(self, field.name))
        return zip(field_names, field_values)


class Datapoint(DatapointTemplate, ModelWithIterableFields):
    """
    Similar to the generic Datapoint model (see docstring in DatapointTemplate
    for more information).
    """

    # Overload the docstring with the one of DatapointTemplate for the
    # automatic generation of documentation in schema, as the original
    # docstring contains more general descriptions.
    __doc__ = DatapointTemplate.__doc__.strip()


class DatapointValue(DatapointValueTemplate):
    """
    Similar to the generic DatapointValue model (see docstring in
    DatapointValueTemplate for more information) but with the correct
    Datapoint model linked to it.
    """

    # Overload the docstring with the one of DatapointValueTemplate for
    # the automatic generation of documentation in schema, as the original
    # docstring contains more general descriptions.
    __doc__ = DatapointValueTemplate.__doc__.strip()
    #
    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=("The datapoint that the value message belongs to."),
    )


class DatapointSchedule(DatapointScheduleTemplate):
    """
    Similar to the generic DatapointSchedule model (see docstring in
    DatapointScheduleTemplate for more information) but with the correct
    Datapoint model linked to it.
    """

    # Overload the docstring with the one of DatapointScheduleTemplate for
    # the automatic generation of documentation in schema, as the original
    # docstring contains more general descriptions.
    __doc__ = DatapointScheduleTemplate.__doc__.strip()
    #
    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=("The datapoint that the schedule message belongs to."),
    )


class DatapointSetpoint(DatapointSetpointTemplate):
    """
    Similar to the generic DatapointSetpoint model (see docstring in
    DatapointSetpointTemplate for more information) but with the correct
    Datapoint model linked to it.
    """

    # Overload the docstring with the one of DatapointSetpointTemplate for
    # the automatic generation of documentation in schema, as the original
    # docstring contains more general descriptions.
    __doc__ = DatapointSetpointTemplate.__doc__.strip()
    #
    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=("The datapoint that the setpoint message belongs to."),
    )
