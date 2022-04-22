from asgiref.sync import async_to_sync
from datetime import datetime
import json
import logging
from urllib import parse as urlparse

from channels.generic.websocket import JsonWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from django.db.models.signals import post_save

from .models import Datapoint
from .apps import EmpAppsCache
from esg.utils.timestamp import datetime_to_pretty_str

logger = logging.getLogger(__name__)


class DatapointUpdate(JsonWebsocketConsumer):
    """
    A consumer that sends updates of Datapoint fields via websocket to the
    user.

    Manuelly test with:
    Execute in browser development console:
        ws = new WebSocket("ws://localhost:8000/ws/datapoint-update/?datapoint-ids=[1,2]");
        ws.onmessage = function(msg){console.log(JSON.parse(msg.data))}
    Change the value of http://localhost:8000/admin/emp_main/datapoint/
    in the admin panel.
    """

    def connect(self):
        """
        Accept every connection and compute the ids of datapoints the user is
        permitted to receive updates for.
        """
        self.user = self.scope["user"]
        self.accept()
        logger.debug(
            "DatapointUpdate consumer accepted connection from user=%s",
            self.user,
        )

        # Parse the set of requested datapoints from the query string.
        try:
            query_string = self.scope["query_string"].decode("utf8")
            query_string_parsed = urlparse.parse_qs(query_string)
            # if the query string looks like this: ?datapoint-ids=[1,2]"
            # then the query_string_parsed object looks like this:
            # {'datapoint-ids': ['[1,2]']}
            datapoint_ids_qs_json = query_string_parsed["datapoint-ids"][0]
            requested_dp_ids = set(json.loads(datapoint_ids_qs_json))
        except:
            logging.exception(
                "DatapointUpdate consumer received object not translatable "
                "into requested datapoint ids by user=%s.",
                self.user,
            )
            raise

        # Compute the set of all datapoint ids for which the user has
        # permissions.
        apps_cache = EmpAppsCache.get_instance()
        dp_ids = apps_cache.get_allowed_datapoint_ids_for_user(self.user)
        all_allowed_dp_ids = set(dp_ids)

        # Update permitted ids to trigger that updates for those datapoints
        # are forwarded to the client.
        permitted_ids = all_allowed_dp_ids.intersection(requested_dp_ids)
        self.permitted_datapoint_ids = permitted_ids
        logger.debug(
            "DatapointUpdate consumer updated permitted ids for user=%s "
            "to datapoints=%s",
            *(self.user, permitted_ids)
        )

        # Check if the client requested ids he has no permissions for.
        # This should usually not happen if a user opens a normal web page
        # but only if people start playing around with the websocket manually.
        denied_ids = requested_dp_ids.difference(all_allowed_dp_ids)
        if denied_ids:
            logger.warning(
                "DatapointUpdate consumer denied user=%s access to the"
                "datapoints=%s",
                *(self.user, denied_ids)
            )

        # Connect to datapoint signal so this consumer can send the updated
        # data of that datapoint to the user. Use a dispatch uid for signals,
        # so we disconnect from the correct signal on disconnect.
        self.post_save_uid = "post_save" + str(id(self))
        post_save.connect(
            self.send_datapoint_update_to_client,
            sender=Datapoint,
            dispatch_uid=self.post_save_uid,
        )

    def send_datapoint_update_to_client(self, sender, **kwargs):
        """
        Sends a JSON version of a changed datapoint via Websocket to the
        lient.

        TODO: Use a proper serializer.
        """
        logger.debug("DatapointUpdate consumer got datapoint update %s", kwargs)

        # Be aware that this datapoint is not the object from the
        # database but the object that was created by the method that
        # updated or created the datapoint. I.e. if the method wrote a
        # number to a text field it will still be a number here. If that is an
        # issue you can circumvent this by reloading the object from the DB.
        # Only then the number will be converter to a text.
        datapoint = kwargs["instance"]

        if datapoint.id not in self.permitted_datapoint_ids:
            return
        dp_field_values = {}
        for field in datapoint._meta.fields:
            field_value = getattr(datapoint, field.name)
            # JSON can't carry datetime objects.
            if isinstance(field_value, datetime):
                field_value = datetime_to_pretty_str(field_value)

            dp_field_values[field.name] = field_value
        self.send_json(dp_field_values)

    def disconnect(self, close_code):
        """
        Disconnect from signal.
        """
        # Apparently it is necessary to use the exact same arguments as for
        # connect here to disconnect successfully.
        post_save.disconnect(
            self.send_datapoint_update_to_client,
            sender=Datapoint,
            dispatch_uid=self.post_save_uid,
        )
        logger.debug(
            "DatapointUpdate consumer disconnected for user=%s", self.user
        )


class DatapointLatestConsumer(WebsocketConsumer):

    groups = ["datapoint.latest"]

    def connect(self):
        if "user" in self.scope:
            self.user = self.scope["user"]
        else:
            logger.warning(
                "No user in scope. Be alerted if this is not a "
                "call from emp_main/tests/test_consumer.py!"
            )
            self.user = None

        self.accept()

        logger.debug(
            "DatapointUpdate consumer accepted connection from user=%s",
            self.user,
        )

    def datapoint_latest(self, message):
        print("message", message)
        self.send(message["text"])

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "datapoint.latest", self.channel_name
        )
