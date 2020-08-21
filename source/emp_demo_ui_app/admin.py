from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import DemoAppPage


@admin.register(DemoAppPage)
class DemoAppPageAdmin(GuardedModelAdmin):
    """
    A simple example for an Django admin configuration of DempAppPage models.

    This admin instance allows you to set up per object level permissions,
    i.e. to control for each page of the demo app which users will be able
    to access it.
    """
    #  Just convenience. Automatically fill the page_slug field.
    prepopulated_fields = {
        "page_slug": ("page_name",)
    }

    # Configure the list view in the admin page.
    list_display = (
        "id",
        "page_name",
        "page_slug",
    )
    list_display_links = (
        "page_name",
    )
