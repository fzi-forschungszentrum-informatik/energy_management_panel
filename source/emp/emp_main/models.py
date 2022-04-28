from django.db import models

from esg.django_models.datapoint import DatapointTemplate
from esg.django_models.datapoint import ValueMessageTemplate
from esg.django_models.datapoint import LastValueMessageTemplate
from esg.django_models.datapoint import SetpointMessageTemplate
from esg.django_models.datapoint import LastSetpointMessageTemplate
from esg.django_models.datapoint import ScheduleMessageTemplate
from esg.django_models.datapoint import LastScheduleMessageTemplate
from esg.django_models.metadata import GeographicPositionTemplate
from esg.django_models.metadata import PlantTemplate


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


class ValueMessage(ValueMessageTemplate):
    """
    Similar to the generic ValueMessage model (see docstring in
    ValueMessageTemplate for more information) but with the correct
    Datapoint model linked to it.
    """

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=("The datapoint that the value message belongs to."),
    )


class LastValueMessage(LastValueMessageTemplate):
    """
    Similar to the generic LastValueMessage model (see docstring in
    LastValueMessageTemplate for more information) but with the correct
    Datapoint model linked to it.
    """

    datapoint = models.OneToOneField(
        Datapoint,
        on_delete=models.CASCADE,
        related_name="last_value_message",
        help_text=("The datapoint that the value message belongs to."),
    )


class ScheduleMessage(ScheduleMessageTemplate):
    """
    Similar to the generic ScheduleMessage model (see docstring in
    ScheduleMessageTemplate for more information) but with the correct
    Datapoint model linked to it.
    """

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=("The datapoint that the schedule message belongs to."),
    )


class LastScheduleMessage(LastScheduleMessageTemplate):
    """
    Similar to the generic LastScheduleMessage model (see docstring in
    LastScheduleMessageTemplate for more information) but with the correct
    Datapoint model linked to it.
    """

    datapoint = models.OneToOneField(
        Datapoint,
        on_delete=models.CASCADE,
        related_name="last_schedule_message",
        help_text=("The datapoint that the schedule message belongs to."),
    )


class SetpointMessage(SetpointMessageTemplate):
    """
    Similar to the generic SetpointMessage model (see docstring in
    SetpointMessageTemplate for more information) but with the correct
    Datapoint model linked to it.
    """

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=("The datapoint that the setpoint message belongs to."),
    )


class LastSetpointMessage(LastSetpointMessageTemplate):
    """
    Similar to the generic LastSetpointMessage model (see docstring in
    LastSetpointMessageTemplate for more information) but with the correct
    Datapoint model linked to it.
    """

    datapoint = models.OneToOneField(
        Datapoint,
        on_delete=models.CASCADE,
        related_name="last_setpoint_message",
        help_text=("The datapoint that the setpoint message belongs to."),
    )


class Plant(PlantTemplate):
    """
    Create instance of model template.
    """

    pass


class GeographicPosition(GeographicPositionTemplate):
    """
    Create instance of model template.
    """

    plant = models.OneToOneField(
        Plant, on_delete=models.CASCADE, related_name="_geographic_position"
    )
