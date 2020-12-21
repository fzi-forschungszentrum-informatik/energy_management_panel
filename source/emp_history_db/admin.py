from django.contrib import admin

from .models import DatapointValue, DatapointSetpoint, DatapointSchedule

@admin.register(DatapointValue)
class DatapointValueAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "datapoint",
        "timestamp",
        "value",
    )
    list_filter = (
        "datapoint",
    )
    readonly_fields = (
        "id",
    )

@admin.register(DatapointSetpoint)
class DatapointSetpointAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "datapoint",
        "timestamp",
        "setpoint",
    )
    list_filter = (
        "datapoint",
    )
    readonly_fields = (
        "id",
    )

@admin.register(DatapointSchedule)
class DatapointScheduleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "datapoint",
        "timestamp",
        "schedule",
    )
    list_filter = (
        "datapoint",
    )
    readonly_fields = (
        "id",
    )
