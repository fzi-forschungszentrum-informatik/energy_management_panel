from django.urls import path

from .consumers import DatapointUpdate
from .consumers import DatapointMetadataLatestConsumer

# NOTE: consumers expect a trainling slash!
websocket_urlpatterns = [
    path("ws/datapoint-update/", DatapointUpdate.as_asgi()),
    path(
        "ws/datapoint/metadata/latest/",
        DatapointMetadataLatestConsumer.as_asgi(),
    ),
]
