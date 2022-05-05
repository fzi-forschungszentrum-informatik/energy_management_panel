from django.urls import path

from .urls import API_ROOT_PATH
from .consumers import DatapointRelatedLatestConsumer

# NOTE: consumers expect a trainling slash!
websocket_urlpatterns = [
    path("ws/datapoint-update/", DatapointRelatedLatestConsumer.as_asgi()),
    path(
        "ws/" + API_ROOT_PATH + "datapoint/<msg_type>/latest/",
        DatapointRelatedLatestConsumer.as_asgi(),
    ),
]
