"""
"""
from django.urls import path

from .views import LocationView

urlpatterns = [
    path(
        "<slug:location_slug>/",
        LocationView.as_view(
            template_name="./emp_locations/location.html"
        ),
    ),
]
