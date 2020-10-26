import json

from django.db import models
from django.core.exceptions import ValidationError


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


class Datapoint(ModelWithIterableFields):
    """
    Model for a datapoint.

    A datapoint represents one source of information. Devices or Webservices
    will typically emit information on more then one datapoints. E.g. climate
    sensor in a room might publish temperature and humidity measurements. Both
    will be treated as individual datapoints as this allows us to abstract
    away the complexity of the devices.

    TODO: May be replace delete with deactivate, else we will might end with
          entries in the ValueDB with unknown origin (deleted datapoints will
          be rentered but with new id)

    TODO: Add consistency checks on save.
    """

    external_id = models.TextField(
        null=True,
        unique=True,
        blank=True,
        help_text=(
            "This id used if Datapoints data is pushed in from an external tool"
            " (e.g. BEMCom) that maintains it's own list datapoint metadata. "
            "This field allows matching the ids of the external tools with "
            "the database table of the EMP, effectively allowing the EMP "
            "to store Datapoints additionally to what is pushed from the "
            "external tool, e.g. for mock (fake) values."
        )
    )
    short_name = models.SlugField(
        max_length=30,
        null=True,  # required to allow migrating tables without this filed.
        default=None,
        unique=True,
        blank=False,  # New datappoints should not have an empty short_name
        help_text=(
            "A short name to identify the datapoint."
        )
    )
    TYPE_CHOICES = [
        ("sensor", "Sensor"),
        ("actuator", "Actuator"),
    ]
    type = models.CharField(
        max_length=8,
        default=None,
        null=False,
        choices=TYPE_CHOICES,
        help_text=(
            "Datapoint type, can be ether sensor or actuator."
        )
    )
    # Defines the data format of the datapoint, i.e. which additional metadata
    # we can expect to have reasonable values.
    #
    # The formats have the following meanings:
    #   numeric: The value of the datapoint can be stored as a float.
    #   text: The value of the datapoint can be stored as a string.
    #   generic: No additional information.
    #   continuous: The value is a continuous variable with an optional max
    #               and min value, that can take any value in between.
    #   discrete: The value of the datapoint can take one value of limited set
    #             of possible values.
    data_format_choices = [
        ("generic_numeric", "Generic Numeric"),
        ("continuous_numeric", "Continuous Numeric"),
        ("discrete_numeric", "Discrete Numeric"),
        ("generic_text", "Generic Text"),
        ("discrete_text", "Discrete Text"),
    ]
    # Use generic_text as default as it imposes no constraints on the datapoint
    # apart from that the value can be stored as string, which should always
    # be possible as the value has been received as a JSON string.
    data_format = models.CharField(
        max_length=18,
        choices=data_format_choices,
        default="generic_text",
        help_text=(
            "Format of the datapoint value. Additionally defines which meta"
            "data is available for it. See documentation in code for details."
        )
    )
    # Don't limit this, people should never need to use abbreviations or
    # shorten their thoughts just b/c the field is too short.
    description = models.TextField(
        editable=True,
        blank=True,
        help_text=(
            "A human readable description of the datapoint targeted on "
            "users of the API wihtout knowledge about connector details."
        )
    )
    #
    ##########################################################################
    #
    # Below all datapoint fields that may or may not be populated for a
    # particular datapoint depending on the data_format and type.
    #
    ##########################################################################
    #
    last_value = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The last value received for the datapoint. We store all values "
            "including numeric as strings as this simplfies the logic "
            "significantly and prevents unintended side effects, e.g. data "
            "loss if the data format field is changed."
            ""
        )
    )
    last_value_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The timestamp of the last value received via MQTT."
        )
    )
    last_setpoint = models.JSONField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The last schedule received for the datapoint. "
            "Applicable to actuator datapoints."
        )
    )
    last_setpoint_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The timestamp of the last value received for the datapoint."
            "Applicable to actuator datapoints."
        )
    )
    last_schedule = models.JSONField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The last schedule received for the datapoint."
            "Applicable to actuator datapoints."
        )
    )
    last_schedule_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The timestamp of the last value received for the datapoint."
            "Applicable to actuator datapoints."
        )
    )
    allowed_values = models.JSONField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "Allowed values. Applicable to discrete valued datapoints. "
            "Must be a valid JSON string."
        )
    )
    min_value = models.FloatField(
        blank=True,
        null=True,
        default=None,
        help_text=(
            "The minimal expected value of the datapoint. "
            "Applicable to numeric datapoints."
        )
    )
    max_value = models.FloatField(
        blank=True,
        null=True,
        default=None,
        help_text=(
            "The maximal expected value of the datapoint. "
            "Applicable to numeric datapoints."
        )
    )
    unit = models.TextField(
        editable=True,
        default="",
        blank=True,
        help_text=(
            "The unit in SI notation, e.g.  Mg*m*s^-2 aka. kN. "
            "Applicable to numeric datapoints."
        )
    )

    def save(self, *args, **kwargs):
        """
        Replace an empty string in external id with None (which cannot be
        entered directly in the admin), as every None is unique while
        an empty string violates the unique constraint. However, we want
        external id only to be unique if it is set.
        """
        if self.external_id == "":
            self.external_id = None
        super().save(*args, **kwargs)

    def __str__(self):
        if self.short_name is not None:
            return (str(self.id) + " - " + self.short_name)
        else:
            return str(self.id)
