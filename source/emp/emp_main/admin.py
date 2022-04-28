from django import forms, db
from django.contrib import admin

from .models import Datapoint
from .models import ValueMessage
from .models import LastValueMessage
from .models import SetpointMessage
from .models import LastSetpointMessage
from .models import ScheduleMessage
from .models import LastScheduleMessage
from .models import GeographicPosition
from .models import Plant
from esg.utils.timestamp import datetime_to_pretty_str


class LastValueMessageInline(admin.TabularInline):
    model = LastValueMessage
    verbose_name_plural = "Last Value Message"
    fields = ("value", "time")


class LastScheduleMessageInline(admin.TabularInline):
    model = LastScheduleMessage
    verbose_name_plural = "Last Schedule Message"
    fields = ("schedule", "time")
    # Readonly as sensors have no schedules and we shouldn't allow
    # the admin to create any at will.
    readonly_fields = fields
    can_delete = False


class LastSetpointMessageInline(admin.TabularInline):
    model = LastSetpointMessage
    verbose_name_plural = "Last Setpoint Message"
    fields = ("setpoint", "time")
    # Readonly as sensors have no setpoints and we shouldn't allow
    # the admin to create any at will.
    readonly_fields = fields
    can_delete = False


@admin.register(Datapoint)
class DatapointAdmin(admin.ModelAdmin):
    """
    Admin model instance for Datapoints.

    TODO: Prevent changing stuff in Admin for external datapoints, like
    e.g. type or data_format. In fact all the fields that are pushed in
    externally.
    """

    list_display = (
        "id",
        "origin",
        "origin_id",
        "type",
        "data_format",
        "short_name",
        "description",
        "unit",
        "last_value_truncated",
        "last_value_timestamp_pretty",
    )
    list_display_links = ("id",)
    list_editable = (
        "data_format",
        "short_name",
        "description",
        "unit",
    )
    list_filter = (
        "origin",
        "type",
        "data_format",
        ("short_name", admin.EmptyFieldListFilter),
    )
    # GOTCHA: Be aware that this setting also affects the search of the
    # `autocomplete_fields` for any Admin page that autocomplete to select
    # datapoints, e.g. like `ValueMessageAdmin` does.
    search_fields = (
        "origin_id",
        "short_name",
        "description",
    )
    readonly_fields = (
        "id",
        "origin",
        "origin_id",
        "last_value_truncated",
        "last_value_timestamp_pretty",
    )
    inlines = [
        LastValueMessageInline,
        LastScheduleMessageInline,
        LastSetpointMessageInline,
    ]

    def last_value_timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        if hasattr(obj, "last_value_message"):
            ts = obj.last_value_message.time
            if ts is not None:
                return datetime_to_pretty_str(ts)
        return "-"

    last_value_timestamp_pretty.admin_order_field = "last_value_timestamp"
    last_value_timestamp_pretty.short_description = "Last value timestamp"

    def last_value_truncated(self, obj):
        """
        Return a possible truncated value if the last value is very long.
        """
        value = "-"
        if hasattr(obj, "last_value_message"):
            if obj.last_value_message.value is not None:
                value = str(obj.last_value_message.value)

        truncation_length = 100
        if len(value) >= truncation_length:
            value = value[:truncation_length] + " [truncated]"
        return value

    last_value_truncated.admin_order_field = "last_value"
    last_value_truncated.short_description = "last_value"

    def get_fieldsets(self, request, obj=None):
        """
        Dynamically add fields that are only relevant for specific values
        of data_format or additional fields for actuators.
        """
        # obj is None while adding a datapoint in the admin UI.
        if obj is not None:
            generic_metadata_fields = ["id"]
        else:
            generic_metadata_fields = []

        generic_metadata_fields.extend(
            [
                "short_name",
                "origin",
                "origin_id",
                "type",
                "data_format",
                "description",
            ]
        )

        data_format_specific_fields = []
        if obj is not None:
            if " Numeric" in obj.data_format:
                data_format_specific_fields.append("unit")
            if "Discrete " in obj.data_format:
                data_format_specific_fields.append("allowed_values")
            if "Continuous Numeric" in obj.data_format:
                data_format_specific_fields.append("min_value")
                data_format_specific_fields.append("max_value")

        fieldsets = (
            ("GENERIC METADATA", {"fields": generic_metadata_fields}),
            (
                "DATA FORMAT SPECIFIC METADATA",
                {"fields": data_format_specific_fields},
            ),
        )
        return fieldsets

    # Display wider version of normal TextInput for all text fields, as
    # default forms look ugly.
    formfield_overrides = {
        db.models.TextField: {"widget": forms.TextInput(attrs={"size": "60"})},
    }

    """
    Define list view actions below.
    """
    actions = (
        "mark_data_format_as_generic_text",
        "mark_data_format_as_discrete_text",
        "mark_data_format_as_generic_numeric",
        "mark_data_format_as_discrete_numeric",
        "mark_data_format_as_continuous_numeric",
    )

    def mark_data_format_as_generic_text(self, request, queryset):
        """
        Updates data_format for a list of datapoints at once.

        This has no effect on the configuration of services, especially
        Connectors. It is thus fine that the signals wont't fire and the
        save hooks won't be executed.
        """
        queryset.update(data_format="generic_text")

    mark_data_format_as_generic_text.short_description = (
        "Mark data_format of datapoints as generic_text"
    )

    def mark_data_format_as_discrete_text(self, request, queryset):
        """
        Updates data_format. Similar to mark_data_format_as_generic_text
        """
        queryset.update(data_format="discrete_text")

    mark_data_format_as_discrete_text.short_description = (
        "Mark data_format of datapoints as discrete_text"
    )

    def mark_data_format_as_generic_numeric(self, request, queryset):
        """
        Updates data_format. Similar to mark_data_format_as_generic_text
        """
        queryset.update(data_format="generic_numeric")

    mark_data_format_as_generic_numeric.short_description = (
        "Mark data_format of datapoints as generic_numeric"
    )

    def mark_data_format_as_discrete_numeric(self, request, queryset):
        """
        Updates data_format. Similar to mark_data_format_as_generic_text
        """
        queryset.update(data_format="discrete_numeric")

    mark_data_format_as_discrete_numeric.short_description = (
        "Mark data_format of datapoints as discrete_numeric"
    )

    def mark_data_format_as_continuous_numeric(self, request, queryset):
        """
        Updates data_format. Similar to mark_data_format_as_generic_text
        """
        queryset.update(data_format="continuous_numeric")

    def get_changelist_formset(self, request, **kwargs):
        """
        This ensures that when we edit a couple of datapoints in list
        mode we can save and ignore those datapoints that have not been
        touched. If we don't inject these methods the Admin will interpret
        the empty string in short name as string and raise a Validation
        Error, as two emtpy strings are not different (while two None
        values are). Hence we tell the admin to reset the empty strings
        to Nones, which makes the Admin think then that the fields have
        not changed and need not be saved.

        To do so we overload the clean method of the short_name field.
        However accessing this field is only possible after the formset
        has been intialized, which happens shortly before is_valid is
        called. Hence we use an extended is_valid method to inject the
        changed clean function in the short_name form object. See:
        https://github.com/django/django/blob/3.1/django/contrib/admin/options.py#L1758
        """
        formset = super().get_changelist_formset(request, **kwargs)

        def clean(short_name):
            if short_name == "":
                short_name = None
            return short_name

        def is_valid(self):
            for form in self.forms:
                form.fields["short_name"].clean = clean
            return super(type(self), self).is_valid()

        formset.is_valid = is_valid
        return formset


@admin.register(ValueMessage)
class ValueMessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "datapoint",
        "timestamp_pretty",
        "value",
    )
    list_filter = ("datapoint",)
    readonly_fields = ("id",)
    fields = ("datapoint", "value", "time")
    autocomplete_fields = ("datapoint",)

    def timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        ts = obj.time
        if ts is None:
            return "-"
        return datetime_to_pretty_str(ts)

    timestamp_pretty.admin_order_field = "timestamp"
    timestamp_pretty.short_description = "Timestamp"


@admin.register(SetpointMessage)
class SetpointMessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "datapoint",
        "timestamp_pretty",
        "setpoint",
    )
    list_filter = ("datapoint",)
    readonly_fields = ("id",)
    fields = ("datapoint", "value", "setpoint")
    autocomplete_fields = ("datapoint",)

    def timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        ts = obj.time
        if ts is None:
            return "-"
        return datetime_to_pretty_str(ts)

    timestamp_pretty.admin_order_field = "timestamp"
    timestamp_pretty.short_description = "Timestamp"


@admin.register(ScheduleMessage)
class ScheduleMessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "datapoint",
        "timestamp_pretty",
        "schedule",
    )
    list_filter = ("datapoint",)
    readonly_fields = ("id",)
    fields = ("datapoint", "value", "schedule")
    autocomplete_fields = ("datapoint",)

    def timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        ts = obj.time
        if ts is None:
            return "-"
        return datetime_to_pretty_str(ts)

    timestamp_pretty.admin_order_field = "timestamp"
    timestamp_pretty.short_description = "Timestamp"


class GeographicPositionInline(admin.TabularInline):
    model = GeographicPosition
    verbose_name_plural = "Geographic Position"


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    inlines = [GeographicPositionInline]
