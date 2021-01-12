from django.contrib import admin
import nested_admin
from guardian.admin import GuardedModelAdmin

from .models import EvaluationSystemPage, PageElement, UIElementContainer, UIElement, Presentation, Chart, Card

"""
Configure the admin pages here.
Nested_admin classes are used to generated multiple layers of nested inlines.
This way the EvaluationSystemPageAdmin can be used as a content management system for the whole page
"""

class ChartInline(nested_admin.NestedStackedInline):
    model = Chart
    extra = 1 
    max_num = 1 #limited to one

class CardInline(nested_admin.NestedStackedInline):
    model = Card
    extra = 1 
    max_num = 1 #limited to one
    #Disables add/change/delete buttons in CardInline
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(CardInline, self).formfield_for_dbfield(
            db_field, request, **kwargs)
        if db_field.name == 'card_button_link':
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False  # default is already False
        return formfield

class PresentationInline(nested_admin.NestedStackedInline):
    model = Presentation
    extra = 1
    max_num = 1 #limited to one

    #Only one of the inlines is visible. Presentation type is choosen via dropdown.
    inlines = [ChartInline, CardInline] 
    
    #Disables add/change/delete buttons in PresentationInline
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(PresentationInline, self).formfield_for_dbfield(
            db_field, request, **kwargs)
        if db_field.name == 'datapoint':
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False  # default is already False
        return formfield

# Distinguish between UIElementInContainerInline and UIElementInPageElementInline
# UIElementInContainerInline is used in containers. Any number of UIElements can be added in containers
# UIElementInPageElementInline is used outside containers. There only one UIElement can be added.
class UIElementInContainerInline(nested_admin.NestedStackedInline):
    model = UIElement
    extra = 0
    inlines = [PresentationInline]
    exclude = ['page_element']

class UIElementInPageElementInline(nested_admin.NestedStackedInline):
    model = UIElement
    extra = 1
    max_num = 1 #limited to one
    inlines = [PresentationInline]  
    exclude = ['container_element']
    

class UIElementContainerInline(nested_admin.NestedStackedInline):
    model = UIElementContainer
    extra = 1
    max_num = 1
    inlines = [UIElementInContainerInline]

    #Disables add/change/delete buttons in UIElementContainerInline
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(UIElementContainerInline, self).formfield_for_dbfield(
            db_field, request, **kwargs)
        if db_field.name == 'container_dropdown_links':
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
        return formfield


class PageElementInline(nested_admin.NestedStackedInline):
    model = PageElement
    extra = 0

    #Only one of the inlines is visible. PageElement type is choosen via dropdown.
    inlines = [UIElementContainerInline, UIElementInPageElementInline] 

@admin.register(EvaluationSystemPage)
class EvaluationSystemPageAdmin(nested_admin.NestedModelAdmin, GuardedModelAdmin):
    """
    Django admin configuration for EvaluationSystemPages
    GuardedModelAdmin instance allows you to set up per object level permissions,
    NestedModelAdmin instance allows to nest multiple layers of inlines.
    This admin configuration allows to build a whole page from scretch with only this admin.
    """
    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js', # jquery #TODO durch django jquery ersetzen
            'emp_evaluation_system/js/page_admin.js',
        )

    site_header = "Wow amazing title"

    list_display = (
        "string_representation",
        "description"
    )

    inlines = [PageElementInline]

    #  Just convenience. Automatically fill the page_slug field.
    prepopulated_fields = {
        "page_slug": ("page_name",)
    }

    def string_representation(self, obj):
        return obj

admin.site.site_header = 'EMP Evaluation System Admin'
admin.site.site_title = 'EMP Evaluation System Admin'

