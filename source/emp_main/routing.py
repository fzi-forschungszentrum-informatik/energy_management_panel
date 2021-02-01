from django.urls import path

from .consumers import DatapointUpdate


websocket_urlpatterns = [
    path(
        "ws/datapoint-update/",
        DatapointUpdate.as_asgi(),
    ),
]

