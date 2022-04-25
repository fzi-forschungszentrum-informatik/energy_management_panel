#!/usr/bin/env python3
"""
"""
from django.test import TestCase
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from emp_main.consumers import DatapointRelatedLatestConsumer


class TestDatapointRelatedLatestConsumer(TestCase):
    """
    Tests for `emp_main.consumers.DatapointRelatedLatestConsumer`
    """

    ws_url = "/ws/api/datapoint/metadata/latest/?datapoint-ids=[1,2]"

    async def test_update_received(self):
        """
        Verify that an update send over the channels group is received on
        websocket.
        """
        communicator = WebsocketCommunicator(
            DatapointRelatedLatestConsumer.as_asgi(), self.ws_url
        )

        connected, _ = await communicator.connect()
        assert connected

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "datapoint.metadata.latest.1",
            {"type": "datapoint.related", "json": "test"},
        )

        response = await communicator.receive_from()

        assert response == "test"
