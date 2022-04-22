from django.urls import path

from .consumers import DatapointUpdate
from .consumers import DatapointLatestConsumer

# NOTE: consumers expect a trainling slash!
websocket_urlpatterns = [
    path("ws/datapoint-update/", DatapointUpdate.as_asgi()),
    path("ws/datapoint/latest/", DatapointLatestConsumer.as_asgi()),
]
