from django.contrib import admin

from .models import DatapointValue

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
