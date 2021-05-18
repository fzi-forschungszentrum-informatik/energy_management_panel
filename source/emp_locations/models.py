from django.db import models
from django.contrib.contenttypes.models import ContentType

from .apps import app_url_prefix
from emp_main.models import Datapoint


class Location(models.Model):
    """
    Model for Locations like room numbers used to organize the EMP.
    """
    name = models.CharField(
        max_length=18,
        unique=True,
        help_text=(
            "The name of the page (i.e. location) as displayed in the navbar, "
            "e.g. 3.1.07. Should not exceed 18 chars, as the string will be "
            "wider then the available space in the navbar."
            )
        )

    slug = models.SlugField(
        unique=True,
        help_text=(
            "The name of the page used in the URL of it. Must be unique "
            "as two pages of this app cannot have the same URL."
        )
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        u = "/" + app_url_prefix + "/" + self.slug + "/"
        return u

class Widget(models.Model):
    """
    Base class for Widgets, store common functionality here.

    This class uses additions to define concrete Widgets,
    while still allowing to find all widgets in one table.
    """

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
    )
    type_choices = [
        ("climate", "Climate"),
        ("temperature_control", "Temperature Control"),
        ("occupancy", "Occupancy"),
    ]

    app_label = Location._meta.app_label
    addition_models = {
        "climate": {
            "app_label": app_label,
            "model": "climatewidgetaddition",
        },
        "temperature_control": {
            "app_label": app_label,
            "model": "temperaturecontrolwidgetaddition",
        },
        "occupancy": {
            "app_label": app_label,
            "model": "occupancywidgetaddition",
        },
    }
    type = models.CharField(
        max_length=30,
        choices=type_choices,
        default="climate",
    )

    def __str__(self):
        return "%s (%s)" % (self.type, self.location)

    def save(self, *args, **kwargs):
        if not self.id:
            super(Widget, self).save(*args, **kwargs)
            try:
                if self.type in self.addition_models:
                    ct_kwargs = self.addition_models[self.type]
                    addition_type = ContentType.objects.get(**ct_kwargs)
                    addition_model = addition_type.model_class()
                    addition_model(
                        widget=self,
                    ).save()
            except Exception:
                Widget.objects.get(id=self.id).delete()
                raise
            return
        type_as_in_db = Widget.objects.get(id=self.id).type
        if type_as_in_db == self.type:
            super(Widget, self).save(*args, **kwargs)
            return
        if type_as_in_db in self.addition_models:
            ct_kwargs = self.addition_models[type_as_in_db]
            addition_type = ContentType.objects.get(**ct_kwargs)
            addition_model = addition_type.model_class()
            addition_model.objects.get(widget=self.id).delete()

        if self.type in self.addition_models:
            ct_kwargs = self.addition_models[self.type]
            addition_type = ContentType.objects.get(**ct_kwargs)
            addition_model = addition_type.model_class()
            addition_model(
                widget=self,
            ).save()

        super(Widget, self).save(*args, **kwargs)

    def get_addition_model(self,  _type=None):
        if _type is None:
            _type = self.type

        if _type not in self.addition_models:
            addition_model = None
        else:
            ct_kwargs = self.addition_models[_type]
            addition_type = ContentType.objects.get(**ct_kwargs)
            addition_model = addition_type.model_class()
        return addition_model

    def get_addition_object(self):
        addition_model = self.get_addition_model()
        if addition_model is None:
            addition_object = None
        else:
            addition_object = addition_model.objects.get(
                widget_id=self.id
            )
        return addition_object


class GenericWidgetAddition(models.Model):
    """
    Base class for additions, holds generic components.
    """

    class Meta:
        abstract = True

    widget = models.OneToOneField(
        Widget,
        on_delete=models.CASCADE,
        primary_key=True,
        editable=False,
    )

    def get_detail(self):
        """
        Returns the Detail config, creates no detail by default.

        Returns:
        --------
        Detail : class
            A class that dynamically configures the detail template.
        """
        class Detail:
            is_active = False
            has_custom_tab = False
            has_plot_tab = False
            has_datapoint_tab = False
        Detail.html_id = "widget_detail_" + str(self.widget.id)
        Detail.datapoints_for_tab = []
        return Detail


class ClimateWidgetAddition(GenericWidgetAddition):

    temperature = models.ForeignKey(
        Datapoint,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        # Disable backwards relation from datapoint to the WidgetAddtion,
        # This does not seem very useful at all.
        related_name="+",
        help_text=(
            "The datapoint holding the temperature value of the location."
        )
    )
    humidity = models.ForeignKey(
        Datapoint,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="+",
        help_text=(
            "The datapoint holding the humidity value of the location."
        )
    )

    def get_detail(self):
        """
        Returns the Detail config, creates no detail by default.

        Returns:
        --------
        Detail : class
            A class that dynamically configures the detail template.
        """
        class Detail:
            is_active = True
            has_custom_tab = True
            has_plot_tab = False
            has_datapoint_tab = True
        Detail.html_id = "widget_detail_" + str(self.widget.id)
        Detail.datapoints_for_tab = [self.humidity, self.temperature]
        return Detail

class TemperatureControlWidgetAddition(GenericWidgetAddition):

    temperature_measured = models.ForeignKey(
        Datapoint,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="+",
        help_text=(
            "The datapoint holding the temperature value of the location."
        )
    )
    temperature_setpoint = models.ForeignKey(
        Datapoint,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="+",
        help_text=(
            "The datapoint used for sending the setpoint."
        )
    )

class OccupancyWidgetAddition(GenericWidgetAddition):
    """
    This model needs some additional fields (and probably logic too) to
    handle some form of calendar data.
    """

    def get_detail(self):
        """
        Returns the Detail config, creates no detail by default.

        Returns:
        --------
        Detail : class
            A class that dynamically configures the detail template.
        """
        class Detail:
            is_active = True
            has_custom_tab = False
            has_plot_tab = False
            has_datapoint_tab = False
        Detail.html_id = "widget_detail_" + str(self.widget.id)
        Detail.datapoints_for_tab = []
        return Detail
