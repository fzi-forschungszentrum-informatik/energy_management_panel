#!/usr/bin/env python3
"""
"""
from django.test import Client
from django.test import TransactionTestCase

from emp_main.models import Datapoint as DatapointDb

API_ROOT_PATH = "/api"

"""
Test data for all the tests. This is pretty redundant to esg.test.data but
kept divided to prevent nasty side effects when changing data in the esg
package.
"""
TEST_DATAPOINTS = [
    # The minimum amount of information forming a valid datapoint.
    {
        # fmt: off
        "Python": {
            "id": 1,
            "type": "Sensor",
        },
        # fmt: on
        "JSONable": {
            "id": 1,
            "origin": None,
            "origin_id": None,
            "short_name": None,
            "type": "Sensor",
            "data_format": "Unknown",
            "description": "",
            "allowed_values": None,
            "min_value": None,
            "max_value": None,
            "unit": "",
        },
    },
    # Fields populated with non-default values.
    {
        # fmt: off
        "Python": {
            "id": 2,
            "origin": "HoLL BEMCom Instance",
            "origin_id": "42",
            "short_name": "T_zone_f",
            "type": "Actuator",
            "data_format": "Continuous Numeric",
            "description": "Setpoint temperature first floor.",
            "allowed_values": None,
            "min_value": 13.37,
            "max_value": 42.0,
            "unit": "°C",
        },
        # fmt: on
        "JSONable": {
            "id": 2,
            "origin": "HoLL BEMCom Instance",
            "origin_id": "42",
            "short_name": "T_zone_f",
            "type": "Actuator",
            "data_format": "Continuous Numeric",
            "description": "Setpoint temperature first floor.",
            "allowed_values": None,
            "min_value": 13.37,
            "max_value": 42.0,
            "unit": "°C",
        },
    },
    # Allowed values set with JSON encoded floats..
    {
        # fmt: off
        "Python": {
            "id": 3,
            "type": "Sensor",
            "data_format": "Discrete Numeric",
            "allowed_values": [21.0, 21.5, 22.0],
        },
        # fmt: on
        "JSONable": {
            "id": 3,
            "origin": None,
            "origin_id": None,
            "short_name": None,
            "type": "Sensor",
            "data_format": "Discrete Numeric",
            "description": "",
            "allowed_values": ["21.0", "21.5", "22.0"],
            "min_value": None,
            "max_value": None,
            "unit": "",
        },
    },
]


class TestDatapoint(TransactionTestCase):
    """
    Tests for the TODO.
    """

    def tearDown(self):
        """
        Delete all datapoints after each tests to prevent unique constraints
        from short_name.
        """
        DatapointDb.objects.all().delete()

    def _create_test_datapoints_in_db(self):
        """
        helper function to prevent redundant code.
        """
        for test_datapoint in TEST_DATAPOINTS:
            dp = DatapointDb.objects.create(**test_datapoint["Python"])
            dp.save()

    def test_get_datapoint(self):
        """
        Verify that GET /datapoint/ endpoint retrieves datapoint metadata.
        """
        self._create_test_datapoints_in_db()

        client = Client()
        response = client.get(API_ROOT_PATH + "/datapoint/")

        assert response.status_code == 200

        expected_jsonable = {}
        for test_datapoint in TEST_DATAPOINTS:
            expected_id = str(test_datapoint["Python"]["id"])
            expected_jsonable[expected_id] = test_datapoint["JSONable"]

        actual_jsonable = response.json()

        assert expected_jsonable == actual_jsonable

    def test_post_datapoint(self):
        """
        Verify that post stores in DB and publishes on channel.
        """
