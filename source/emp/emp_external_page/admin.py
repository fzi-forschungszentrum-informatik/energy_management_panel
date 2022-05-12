#!/usr/bin/env python3
"""
"""
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import ExternalPage
from .models import ExternalPageGroup


@admin.register(ExternalPageGroup)
class ExternalPageGroupAdmin(GuardedModelAdmin):

    prepopulated_fields = {"slug": ("name",)}
    list_display = (
        "id",
        "name",
        "slug",
    )
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(ExternalPage)
class ExternPageAdmin(GuardedModelAdmin):

    prepopulated_fields = {"slug": ("name",)}
    list_display = (
        "id",
        "group",
        "name",
        "slug",
        "src",
    )
    list_editable = list_display[1:]
    autocomplete_fields = ("group",)
