from django.conf import settings
from django.urls import path

from .urls import API_ROOT_PATH
from .consumers import DatapointRelatedLatestConsumer

WS_ROOT_PATH = settings.ROOT_PATH

# NOTE: consumers expect a trainling slash!
websocket_urlpatterns = [
    path(
        WS_ROOT_PATH + "ws/datapoint-update/",
        DatapointRelatedLatestConsumer.as_asgi(),
    ),
    path(
        WS_ROOT_PATH + "ws/" + API_ROOT_PATH + "datapoint/<msg_type>/latest/",
        DatapointRelatedLatestConsumer.as_asgi(),
    ),
]
