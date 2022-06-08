from django.contrib import admin
from django import forms, db
from django.contrib.admin.widgets import AutocompleteSelect
from guardian.admin import GuardedModelAdmin

from .models import EnergyFlow, Widget, Flow


@admin.register(EnergyFlow)
class EnergyFlowAdmin(GuardedModelAdmin):
    list_display = [
        "id",
        "name",
        "is_active",
        "slug",
    ]
    list_editable = list_display[1:]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "energyflow",
        "is_active",
        "grid_position_left",
        "grid_position_right",
        "grid_position_top",
        "grid_position_bottom",
        "icon_url",
    ]
    list_editable = list_display[1:]
    list_filter = [
        "energyflow",
        "is_active",
    ]
    autocomplete_fields = [
        "datapoint1",
        "datapoint2",
    ]

    def energyflow(self, obj):
        obj.energyflow.name


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "energyflow",
        "origin_device",
        "target_device",
        "flow_color",
        "value_datapoint",
    ]
    list_editable = list_display[1:]
    list_filter = [
        "energyflow",
        "flow_color",
    ]
    autocomplete_fields = [
        "value_datapoint",
    ]

    def energyflow(self, obj):
        obj.energyflow.name


# This should make the autocomplete form wider, but the AutocompleteMixin
# seems to ignore the attr setting.
#
#    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        if db_field.name in self.get_autocomplete_fields(request):
#            kwargs['widget'] = AutocompleteSelect(
#                db_field.remote_field,
#                self.admin_site,
#                using=kwargs.get('using'),
#                attrs={'size': '160'}
#            )
#        return super().formfield_for_foreignkey(db_field, request, **kwargs)
