"""
For the demo UI pages it is sufficient to provide all pages with a single view.
The only necessary parameter is thereby the page_slug (e.g. the "test-page-1"
in http://localhost:8000/demo/test-page-1/) which is used to retrieve the page
specific content from the DB.
"""
from django.urls import path

from .views import DemoUIPageView

urlpatterns = [
    path(
        "<slug:page_slug>/",
        DemoUIPageView.as_view(
            template_name="./emp_demo_ui_app/demo_page.html"
        ),
    ),
]
