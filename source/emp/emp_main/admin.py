import json
from django import forms, db
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Datapoint
from .models import DatapointValue
from .models import DatapointSetpoint
from .models import DatapointSchedule
from ems_utils.timestamp import datetime_to_pretty_str


@admin.register(Datapoint)
class DatapointAdmin(admin.ModelAdmin):
    """
    Admin model instance for Datapoints.

    TODO: Prevent changing stuff in Admin for external datapoints, like
    e.g. type or data_format. In fact all the fields that are pushed in
    externally.
    """

    list_display = (
        "string_representation",
        "type",
        "data_format",
        "description",
        "last_value",
        "last_value_timestamp_pretty",
    )
    list_display_links = ("string_representation",)
    list_editable = (
        "description",
        "data_format",
    )
    list_filter = (
        "type",
        "data_format",
    )
    search_fields = (
        "id",
        "origin_id",
        "description",
    )
    readonly_fields = ("id",)

    def string_representation(self, obj):
        return obj

    string_representation.short_description = "ID - Short Name"

    def last_value_timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        dt = obj.last_value_timestamp
        if dt is None:
            return "-"
        return datetime_to_pretty_str(dt)

    last_value_timestamp_pretty.admin_order_field = "last_value_timestamp"
    last_value_timestamp_pretty.short_description = "Last value timestamp"

    def last_setpoint_timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        dt = obj.last_setpoint_timestamp
        if dt is None:
            return "-"
        return datetime_to_pretty_str(dt)

    last_setpoint_timestamp_pretty.admin_order_field = "last_setpoint_timestamp"
    last_setpoint_timestamp_pretty.short_description = "Last setpoint timestamp"

    def last_schedule_timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        dt = obj.last_schedule_timestamp
        if dt is None:
            return "-"
        return datetime_to_pretty_str(dt)

    last_schedule_timestamp_pretty.admin_order_field = "last_schedule_timestamp"
    last_schedule_timestamp_pretty.short_description = "Last schedule timestamp"

    def last_schedule_pretty(self, obj):
        """
        Pretty print json of schedule.
        """
        schedule = obj.last_schedule
        if schedule is None:
            return "-"
        try:
            schedule = json.dumps(schedule, indent=4)
            schedule = mark_safe("<pre>" + schedule + "</pre>")

        except Exception:
            pass
        return schedule

    last_schedule_pretty.short_description = "Last schedule"

    def last_setpoint_pretty(self, obj):
        """
        Pretty print json of setpoint.
        """
        setpoint = obj.last_setpoint
        if setpoint is None:
            return "-"

        try:
            setpoint = json.dumps(setpoint, indent=4)
            setpoint = mark_safe("<pre>" + setpoint + "</pre>")

        except Exception:
            pass
        return setpoint

    last_setpoint_pretty.short_description = "Last setpoint"

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
            ["short_name", "origin_id", "type", "data_format", "description",]
        )

        data_format_specific_fields = []
        if obj is not None:
            if "_numeric" in obj.data_format:
                data_format_specific_fields.append("unit")
            if "discrete_" in obj.data_format:
                data_format_specific_fields.append("allowed_values")
            if "continuous_numeric" in obj.data_format:
                data_format_specific_fields.append("min_value")
                data_format_specific_fields.append("max_value")

        last_datapoint_msg_fields = []
        if obj is not None:
            last_datapoint_msg_fields = [
                "last_value",
                "last_value_timestamp",
            ]
            if obj.type == "actuator":
                last_datapoint_msg_fields.extend(
                    [
                        "last_setpoint",
                        "last_setpoint_timestamp",
                        "last_schedule",
                        "last_schedule_timestamp",
                    ]
                )

        fieldsets = (
            ("GENERIC METADATA", {"fields": generic_metadata_fields}),
            ("DATA FORMAT SPECIFIC METADATA", {"fields": data_format_specific_fields}),
            ("LAST DATAPOINT MESSAGES", {"fields": last_datapoint_msg_fields}),
        )
        return fieldsets

    # Display wider version of normal TextInput for all text fields, as
    # default forms look ugly.
    formfield_overrides = {
        db.models.TextField: {"widget": forms.TextInput(attrs={"size": "60"})},
    }


@admin.register(DatapointValue)
class DatapointValueAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "datapoint",
        "timestamp_pretty",
        "value",
    )
    list_filter = ("datapoint",)
    readonly_fields = ("id",)

    def timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        ts = obj.timestamp
        if ts is None:
            return "-"
        return datetime_to_pretty_str(ts)

    timestamp_pretty.admin_order_field = "timestamp"
    timestamp_pretty.short_description = "Timestamp"


@admin.register(DatapointSetpoint)
class DatapointSetpointAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "datapoint",
        "timestamp_pretty",
        "setpoint",
    )
    list_filter = ("datapoint",)
    readonly_fields = ("id",)

    def timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        ts = obj.timestamp
        if ts is None:
            return "-"
        return datetime_to_pretty_str(ts)

    timestamp_pretty.admin_order_field = "timestamp"
    timestamp_pretty.short_description = "Timestamp"


@admin.register(DatapointSchedule)
class DatapointScheduleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "datapoint",
        "timestamp_pretty",
        "schedule",
    )
    list_filter = ("datapoint",)
    readonly_fields = ("id",)

    def timestamp_pretty(self, obj):
        """
        Displays a prettier timestamp format.
        """
        ts = obj.timestamp
        if ts is None:
            return "-"
        return datetime_to_pretty_str(ts)

    timestamp_pretty.admin_order_field = "timestamp"
    timestamp_pretty.short_description = "Timestamp"
