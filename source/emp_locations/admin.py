from django import forms, db
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from .models import Location
from .models import Widget


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )

def create_widget_addition_inlines():
    widget_addition_inlines = {}
    addition_models = Widget.addition_models
    for _type in addition_models.keys():

        ct_kwargs = addition_models[_type]
        addition_type = ContentType.objects.get(**ct_kwargs)
        addition_model = addition_type.model_class()
        model_fields = addition_model._meta.get_fields()
        fields = [f.name for f in model_fields if f.name != "widget"]
        readonly_fields = [f.name for f in model_fields if f.editable is False]

        class WidgetAdditionInline(admin.StackedInline):
            can_delete = False
            verbose_name_plural = "Additional metadata"
        WidgetAdditionInline.model = addition_model
        WidgetAdditionInline.fields = fields
        WidgetAdditionInline.autocomplete_fields = fields
        WidgetAdditionInline.readonly_fields = readonly_fields
        widget_addition_inlines[_type] = WidgetAdditionInline
    return widget_addition_inlines


# TODO: This blocks an inital creation of migrations. Fix this.
widget_addition_inlines = create_widget_addition_inlines()


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
    )
    list_display_links = (
        "__str__",
    )
    list_filter = (
        "type",
        "location",
    )
    search_fields = (
        "type",
    )
    readonly_fields = (
    )
    fieldsets = (
            ('GENERIC CONFIGURATION', {
                "fields": (
                    "type",
                    "location",
                )
            }),
    )

    # Display wider version of normal TextInput for all text fields, as
    # default forms look ugly.
    formfield_overrides = {
        db.models.TextField: {'widget': forms.TextInput(attrs={'size': '60'})},
    }

    def change_view(self, request, object_id, form_url='',
                    extra_context=None):

        type = Widget.objects.get(id=object_id).type
        if type not in widget_addition_inlines:
            self.inlines = ()
        else:
            WidgetAdditionInline = widget_addition_inlines[type]
            self.inlines = (WidgetAdditionInline, )
        return super().change_view(request, object_id)

    def has_add_permission(cls, request):
        return True
