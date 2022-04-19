from django.contrib import admin
import nested_admin
from guardian.admin import GuardedModelAdmin

from .models import EvaluationSystemPage, PageElement, UIElementContainer, UIElement, Presentation, Chart, Card, Metric, Algorithm, ComparisonGraph, ComparisonGraphDataset

"""
Configure the admin pages here.
Nested_admin classes are used to generated multiple layers of nested inlines.
This way the EvaluationSystemPageAdmin can be used as a content management system for the whole page
The Inines are defined in the "wrong" order so the parent Inline can use its children inlines.
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
        if db_field.name == 'datapoint' or db_field.name == 'metric':
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

    #Only one of the inlines is visible (visibility set via page_admin.js). PageElement type is choosen via dropdown.
    inlines = [UIElementContainerInline, UIElementInPageElementInline]

class ComparisonGraphDataInline(nested_admin.NestedStackedInline):
    model = ComparisonGraphDataset
    extra = 1
    max_num = 3

    #Disables add/change/delete buttons in UIElementContainerInline
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(ComparisonGraphDataInline, self).formfield_for_dbfield(
            db_field, request, **kwargs)
        if db_field.name == 'datapoint' or db_field.name == 'metric':
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
        return formfield

class ComparisonGraphInline(nested_admin.NestedStackedInline):
    model = ComparisonGraph
    extra = 0

    inlines = [ComparisonGraphDataInline]

@admin.register(EvaluationSystemPage)
class EvaluationSystemPageAdmin(nested_admin.NestedModelAdmin, GuardedModelAdmin):
    """
    Django admin configuration for EvaluationSystemPages
    GuardedModelAdmin instance allows you to set up per object level permissions,
    NestedModelAdmin instance allows to nest multiple layers of inlines.
    This admin configuration allows to build a whole page from scretch with only this admin.
    """

    #Include js files that manipulate admin
    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js', # jquery 
            'emp_evaluation_system/js/page_admin.js',
        )

    #configure how objects are displayed in tabular 
    list_display = (
        "evaluation_system_page_name",
        "description"
    )

    #Start of the inline recursion
    inlines = [PageElementInline, ComparisonGraphInline]

    #  Just convenience. Automatically fill the page_slug field.
    prepopulated_fields = {
        "page_slug": ("page_name",)
    }

    def evaluation_system_page_name(self, obj):
        return obj

#Set site header and title
admin.site.site_header = 'EMP Evaluation System Admin'
admin.site.site_title = 'EMP Evaluation System Admin'


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = (
        "metric_name",
        "description"
    )

    def metric_name(self, obj):
        return obj

@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description"
    )

    #  Automatically fill the backend_identifier field.
    prepopulated_fields = {
        "backend_identifier": ("name",)
    }

