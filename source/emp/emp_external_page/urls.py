#!/usr/bin/env python3
"""
"""

from django.urls import path

from .views import ExternalPageView

urlpatterns = [
    path(
        "<slug:group_slug>/<slug:page_slug>/",
        ExternalPageView.as_view(
            template_name="./emp_external_page/external_page.html",
        ),
        name="emp_external_page.external_page",
    ),
]
