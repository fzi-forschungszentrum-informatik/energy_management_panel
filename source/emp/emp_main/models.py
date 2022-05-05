from django.db import models

from esg.django_models.datapoint import DatapointTemplate
from esg.django_models.datapoint import ValueMessageTemplate
from esg.django_models.datapoint import LastValueMessageTemplate
from esg.django_models.datapoint import SetpointMessageTemplate
from esg.django_models.datapoint import LastSetpointMessageTemplate
from esg.django_models.datapoint import ScheduleMessageTemplate
from esg.django_models.datapoint import LastScheduleMessageTemplate
from esg.django_models.datapoint import ForecastMessageTemplate
from esg.django_models.metadata import GeographicPositionTemplate
from esg.django_models.metadata import PVSystemTemplate
from esg.django_models.metadata import PlantTemplate
from esg.django_models.metadata import ProductTemplate
from esg.django_models.metadata import ProductRunTemplate


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


class Product(ProductTemplate):
    """
    Create instance of model template.
    """

    pass


class Plant(PlantTemplate):
    """
    Create instance of model template.
    """

    products = models.ManyToManyField(
        Product, blank=True, related_name="_plants"
    )


class GeographicPosition(GeographicPositionTemplate):
    """
    Create instance of model template.
    """

    plant = models.OneToOneField(
        Plant, on_delete=models.CASCADE, related_name="_geographic_position"
    )


class PVSystem(PVSystemTemplate):
    """
    Create instance of model template.
    """

    plant = models.OneToOneField(
        Plant, on_delete=models.CASCADE, related_name="_pv_system",
    )


class ProductRun(ProductRunTemplate):
    """
    Create instance of model template.
    """

    _product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        # Must allow null as field will be null for a short time
        # during saving with `save_from_pydantic`
        null=True,
        related_name="product_runs",
    )
    _plant = models.ForeignKey(
        Plant, on_delete=models.CASCADE, null=True, related_name="product_runs",
    )

    @property
    def product_id(self):
        return self.get_fk_id_from_field(self._product)

    @product_id.setter
    def product_id(self, value):
        self._product = self.set_fk_obj_by_id(value, Product)

    @property
    def plant_id(self):
        return self.get_fk_id_from_field(self._plant)

    @plant_id.setter
    def plant_id(self, value):
        self._plant = self.set_fk_obj_by_id(value, Plant)


class ForecastMessage(ForecastMessageTemplate):
    """
    Django representation of `esg.models.datapoint.ForecastMessage` for
    storing these messages in DB. Subclass to use.
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["datapoint", "time", "product_run"],
                name="Forecast Message Unique.",
            )
        ]

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        related_name="forecast_messages",
        help_text=("The datapoint that the forecast message belongs to."),
    )
    product_run = models.ForeignKey(
        ProductRun,
        on_delete=models.CASCADE,
        related_name="forecast_messages",
        help_text=("The product run that has generated the forecast message."),
    )
