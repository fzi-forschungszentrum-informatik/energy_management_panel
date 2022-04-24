#!/usr/bin/env python3
"""
"""
import asyncio
from copy import deepcopy
from datetime import datetime
from datetime import timezone
import json
from pprint import pformat

from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.http import HttpResponse
from django.test import Client
from django.test import TransactionTestCase

from esg.models.datapoint import DatapointList
from esg.services.base import RequestInducedException

from emp_main.api import GenericAPIView
from emp_main.consumers import DatapointMetadataLatestConsumer
from emp_main.models import Datapoint as DatapointDb
from emp_main.models import ValueMessage as ValueHistoryDb
from emp_main.models import LastValueMessage as ValueLatestDb

API_ROOT_PATH = "/api"

"""
Test data for all the tests. This is pretty redundant to esg.test.data but
kept divided to prevent nasty side effects when changing data in the esg
package.
"""
# The minimum amount of information forming valid datapoints.
# There here are basically there to have something to update in the tests.
TEST_DATAPOINTS_MIN = [
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
    {
        # fmt: off
        "Python": {
            "id": 2,
            "type": "Sensor",
        },
        # fmt: on
        "JSONable": {
            "id": 2,
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
]

# Here a version of the datapoints above that have all fields populated.
TEST_DATAPOINTS = [
    {
        "Python": {
            "id": 1,
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
        "JSONable": {
            "id": 1,
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
    {
        "Python": {
            "id": 2,
            "type": "Sensor",
            "data_format": "Discrete Numeric",
            "allowed_values": [21.0, 21.5, 22.0],
        },
        "JSONable": {
            "id": 2,
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
"""
Define test datasets (i.e. one or more collections of data in different
representations)for `GenericDatapointRelatedAPIViewTests`.

Take care of the following:
`TEST_DATASETS_*_LATEST` and  `TEST_DATASETS_*_HISTORY`:
* Keys `Python_pre_update`, `Python` and `JSONable` exist.
* `Python_pre_update` contains at least one item that is updated with an item
  from `Python`.
* `Python` contains at least one item that is newly created.

`TEST_DATASETS_*_LATEST_INVALID` and  `TEST_DATASETS_*_HISTORY_INVALID`:
* Keys `JSONable`, `status_code_must_be`, `detail_must_contain` exist.
* Try to be as specific as possible with `detail_must_contain` to verify
  that reason why a call failed is the one that was intended while
  developing the tests.
"""
# Define one or more test cases (i.e. full sets of data at different stages
# of processing.
TEST_DATASETS_VALUES_LATEST = [
    {
        "Python_pre_update": [
            {
                "datapoint__id": 1,
                "value": 20.5,
                "time": datetime(2022, 4, 24, 23, 21, 0, tzinfo=timezone.utc),
            },
        ],
        "Python": [
            {
                "datapoint__id": 1,
                "value": 21.0,
                "time": datetime(
                    2022, 4, 24, 23, 21, 32, 100, tzinfo=timezone.utc
                ),
            },
            {
                "datapoint__id": 2,
                "value": True,
                "time": datetime(2022, 4, 24, 23, 21, 25, tzinfo=timezone.utc),
            },
        ],
        "JSONable": {
            "1": {"value": "21.0", "time": "2022-04-24T23:21:32.000100+00:00"},
            "2": {"value": "true", "time": "2022-04-24T23:21:25+00:00"},
        },
    }
]


class TestGenericAPIViewHandleException:
    """
    Tests for emp_main.api.GenericAPIView._handle_exceptions
    """

    def test_non_exception_returned(self):
        """
        If the method doesn't throw an error the decorator should pass the
        result through.
        """

        class Test:
            @GenericAPIView._handle_exceptions
            def test_method(self):
                return HttpResponse(
                    content="test content",
                    status=200,
                    content_type="application/json",
                )

        response = Test().test_method()

        assert isinstance(response, HttpResponse)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.content == b"test content"

    def test_args_and_kwargs_forwarded(self):
        """
        Verify that args and kwargs are forwarded to the payload method.
        """

        class Test:
            @GenericAPIView._handle_exceptions
            def test_method(self, arg, kwarg):
                return HttpResponse(
                    content="arg: {}, kwarg: {}".format(arg, kwarg),
                    status=200,
                    content_type="application/json",
                )

        response = Test().test_method("arg_value", kwarg="kwarg_value")

        assert isinstance(response, HttpResponse)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.content == b"arg: arg_value, kwarg: kwarg_value"

    def test_request_induced_exceptions_yield_400(self):
        """
        Check that `_handle_exceptions` returns a HttpResponse with code 400
        if a method raises RequestInducedException.
        """

        class Test:
            @GenericAPIView._handle_exceptions
            def test_method(self):
                raise RequestInducedException(detail="test detail!")

        response = Test().test_method()

        assert isinstance(response, HttpResponse)
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        assert response.content == b'{"detail": "test detail!"}'

    def test_other_exceptions_yield_500(self):
        """
        Any normal exception should return a 500.
        """

        class Test:
            @GenericAPIView._handle_exceptions
            def test_method(self):
                raise RuntimeError("Rare Exception")

        response = Test().test_method()

        assert isinstance(response, HttpResponse)
        assert response.status_code == 500
        assert response.headers["Content-Type"] == "application/json"
        assert b"internal server error" in response.content

        # Exception details should not be forwarded to the user.
        assert b"RuntimeError" not in response.content
        assert b"Rare Exception" not in response.content


class TestDatapointMetadataAPIView(TransactionTestCase):
    """
    Tests for the the /datapoint/metadata/* endpoints.
    """

    def setUp(self):
        """
        Generic stuff required for all tests.
        """
        self.client = Client()

    def tearDown(self):
        """
        Delete all datapoints after each tests to prevent unique constraints
        from short_name.
        """
        DatapointDb.objects.all().delete()

    def _create_test_datapoints_in_db(self, test_datapoints):
        """
        helper function to prevent redundant code.
        """
        for test_datapoint in test_datapoints:
            dp = DatapointDb.objects.create(**test_datapoint["Python"])
            dp.save()

    def _check_test_datapoints_in_db(self, test_datapoints):
        """
        A utility that checks if a certain datapoints are in DB and have the
        expected fields.
        """
        for test_datapoint in test_datapoints:
            expected_data = test_datapoint["Python"]
            if expected_data["id"] is not None:
                actual_datapoint_db = DatapointDb.objects.get(
                    id=expected_data["id"]
                )
            else:
                actual_datapoint_db = DatapointDb.objects.get(**expected_data)

            for field, expected_value in expected_data.items():

                actual_value = getattr(actual_datapoint_db, field)

                assert_msg = (
                    "Error comparing field `{}` of expected datapoint \n{} "
                    "\n\nwith actual datapoint in db \n{}".format(
                        field,
                        pformat(expected_data, indent=4),
                        pformat(actual_datapoint_db.__dict__, indent=4),
                    )
                )

                assert actual_value == expected_value, assert_msg

    def test_get_datapoint_latest(self):
        """
        Verify that GET /datapoint/metadata/latest/ endpoint retrieves
        datapoint metadata.
        """
        self._create_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS)

        # Ensure the datapoints are stored in DB.
        self._check_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS)

        response = self.client.get(
            API_ROOT_PATH + "/datapoint/metadata/latest/"
        )

        assert response.status_code == 200

        expected_jsonable = {}
        for test_datapoint in TEST_DATAPOINTS:
            expected_id = str(test_datapoint["Python"]["id"])
            expected_jsonable[expected_id] = test_datapoint["JSONable"]

        actual_jsonable = response.json()

        assert expected_jsonable == actual_jsonable

    def _put_test_datapoints(self, test_datapoints):
        """
        Again a utility to prevent redundant code.
        """
        test_datapoints_pydantic = DatapointList.construct_recursive(
            __root__=[m["Python"] for m in test_datapoints]
        )
        test_data = test_datapoints_pydantic.jsonable()
        response = self.client.put(
            API_ROOT_PATH + "/datapoint/metadata/latest/",
            content_type="application/json",
            data=test_data,
        )
        return response

    def test_put_datapoint_latest_creates(self):
        """
        Verify that we can use the put endpoint to store new metadata.
        """
        assert DatapointDb.objects.count() == 0

        # Set IDs to None so we simulate new datapoints.
        test_datapoints = deepcopy(TEST_DATAPOINTS)
        for test_datapoint in test_datapoints:
            test_datapoint["Python"]["id"] = None
            test_datapoint["JSONable"]["id"] = None

        response = self._put_test_datapoints(test_datapoints=test_datapoints)

        assert response.status_code == 200

        # Check that the returned datapoints are as expected. Once more
        # ignore IDs.
        actual_content = []
        ids = []
        for actual_datapoint in json.loads(response.content).values():
            ids.append(actual_datapoint["id"])
            actual_datapoint["id"] = None
            actual_content.append(actual_datapoint)

        for test_datapoint in test_datapoints:
            expected_datapoint = test_datapoint["JSONable"]
            assert expected_datapoint in actual_content

            # Write back the object ID so we can check that the data is in DB.
            id = ids[actual_content.index(expected_datapoint)]
            test_datapoint["Python"]["id"] = id

        # Check the datapoints have reached the DB.
        self._check_test_datapoints_in_db(test_datapoints=test_datapoints)

    def test_put_datapoint_latest_updates(self):
        """
        Verify that we can use the put endpoint to update existing data..
        """
        self._create_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS_MIN)

        # Ensure the datapoints are stored in DB.
        self._check_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS_MIN)

        response = self._put_test_datapoints(test_datapoints=TEST_DATAPOINTS)

        assert response.status_code == 200

        # Check the datapoints have reached the DB.
        self._check_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS)

    def test_put_datapoint_latest_does_not_partially_update(self):
        """
        All or nothing! Verify that no datapoints are saved if one fails.
        """
        self._create_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS_MIN)

        # Ensure the datapoints are stored in DB.
        self._check_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS_MIN)

        # Set one of the test datapoints to a ID that shouldn't exist
        test_datapoints = deepcopy(TEST_DATAPOINTS)
        test_datapoints[1]["Python"]["id"] = 421337
        test_datapoints[1]["JSONable"]["id"] = 421337

        response = self._put_test_datapoints(test_datapoints=test_datapoints)

        # This should have failed and the ID should have been reported.
        assert response.status_code == 400
        assert b"421337" in response.content

        # Finally also verify that the other datapoint has not been saved.
        assert DatapointDb.objects.count() == len(TEST_DATAPOINTS_MIN)
        self._check_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS_MIN)

    def test_put_datapoint_latest_works_for_all_fail(self):
        """
        Test that all non existing datapoints are reported.
        """
        self._create_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS_MIN)

        # Ensure the datapoints are stored in DB.
        self._check_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS_MIN)

        # Set one of the test datapoints to a ID that shouldn't exist
        test_datapoints = deepcopy(TEST_DATAPOINTS)
        test_datapoints[0]["Python"]["id"] = 421336
        test_datapoints[0]["JSONable"]["id"] = 421336
        test_datapoints[1]["Python"]["id"] = 421337
        test_datapoints[1]["JSONable"]["id"] = 421337

        response = self._put_test_datapoints(test_datapoints=test_datapoints)

        assert response.status_code == 400
        assert b"[421336, 421337]" in response.content

    def test_put_datapoint_latest_is_idempotent(self):
        """
        Test that repeated calls work too. Especially here the case when
        updating with data with ID None. This has failed before.
        """
        assert DatapointDb.objects.count() == 0

        # Set IDs to None so we simulate new datapoints.
        test_datapoints = deepcopy(TEST_DATAPOINTS)
        for test_datapoint in test_datapoints:
            test_datapoint["Python"]["id"] = None
            test_datapoint["JSONable"]["id"] = None

        response = self._put_test_datapoints(test_datapoints=test_datapoints)

        assert response.status_code == 200

        response = self._put_test_datapoints(test_datapoints=test_datapoints)

        assert response.status_code == 200

    def test_put_datapoint_latest_publishes_on_channel_group(self):
        """
        Verify that an update send over the channels group is received on
        websocket.
        """
        event_loop = asyncio.get_event_loop()

        # Make sure we have something to update -> know the IDs!
        self._create_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS_MIN)

        self._check_test_datapoints_in_db(test_datapoints=TEST_DATAPOINTS_MIN)

        # Connect to the intended websocket.
        ws_url = "/ws/datapoint/metadata/latest/?datapoint-ids=[1,2]"
        communicator = WebsocketCommunicator(
            DatapointMetadataLatestConsumer.as_asgi(), ws_url
        )

        connected, _ = event_loop.run_until_complete(communicator.connect())
        assert connected

        self._put_test_datapoints(test_datapoints=TEST_DATAPOINTS)

        response1 = json.loads(
            event_loop.run_until_complete(communicator.receive_from())
        )
        response2 = json.loads(
            event_loop.run_until_complete(communicator.receive_from())
        )

        assert response1 == TEST_DATAPOINTS[0]["JSONable"]
        assert response2 == TEST_DATAPOINTS[1]["JSONable"]


class GenericDatapointRelatedAPIViewTests(TransactionTestCase):
    """
    Similar to how `GenericDatapointRelatedAPIView` holds generic code
    for derived APIView classes, this class holds generic tests to derive
    the corresponding test classes.
    """

    RelatedDataLatestModel = None
    RelatedDataHistoryModel = None

    test_data_latest = None
    test_data_history = None

    unique_together_fields_latest = ["datapoint"]
    unique_together_fields_history = ["datapoint__id", "time"]

    def setUp(self):
        """
        Generic stuff required for all tests.
        """
        self.client = Client()

        self.datapoints_by_id = {}
        for test_datapoint in TEST_DATAPOINTS:
            dp = DatapointDb.objects.create(**test_datapoint["Python"])
            dp.save()
            self.datapoints_by_id[dp.id] = dp

    def tearDown(self):
        """
        Delete all datapoints after each tests to prevent unique constraints
        from short_name.
        """
        DatapointDb.objects.all().delete()
        self.RelatedDataLatestModel.objects.all().delete()
        self.RelatedDataHistoryModel.objects.all().delete()

    def _create_test_data_in_db(self, test_data, db_model):
        """
        helper function to prevent redundant code.
        """
        test_data = deepcopy(test_data)
        for test_data_item in test_data:
            # Replace datapoint id with datapoint object, as django wants that.
            if "datapoint__id" in test_data_item:
                datapoint_id = test_data_item.pop("datapoint__id")
                datapoint = DatapointDb.objects.get(id=datapoint_id)
                test_data_item["datapoint"] = datapoint

            obj = db_model.objects.create(**test_data_item)
            obj.save()

    def _check_test_data_exists_in_db(
        self, test_data, db_model, unique_together_fields
    ):
        """
        another helper function to prevent redundant code.
        """
        test_data = deepcopy(test_data)
        for test_data_item in test_data:
            # Replace datapoint id with datapoint object, as django wants that.
            if "datapoint__id" in test_data_item:
                datapoint_id = test_data_item.pop("datapoint__id")
                datapoint = DatapointDb.objects.get(id=datapoint_id)
                test_data_item["datapoint"] = datapoint

            get_args = {f: test_data_item[f] for f in unique_together_fields}
            actual_data_obj = db_model.objects.get(**get_args)

            for field, expected_value in test_data_item.items():

                actual_value = getattr(actual_data_obj, field)

                assert_msg = (
                    "Error comparing field `{}` of expected data item \n{} "
                    "\n\nwith actual item in db \n{}".format(
                        field,
                        pformat(test_data_item, indent=4),
                        pformat(actual_data_obj.__dict__, indent=4),
                    )
                )

                assert actual_value == expected_value, assert_msg


class TestDatapointValueAPIView(GenericDatapointRelatedAPIViewTests):

    RelatedDataLatestModel = ValueLatestDb
    RelatedDataHistoryModel = ValueHistoryDb

    test_datasets_latest = TEST_DATASETS_VALUES_LATEST

    endpoint_url_latest = API_ROOT_PATH + "/datapoint/value/latest/"

    def test_list_latest(self):
        for test_dataset in self.test_datasets_latest:

            self._create_test_data_in_db(
                test_data=test_dataset["Python"],
                db_model=self.RelatedDataLatestModel,
            )

            self._check_test_data_exists_in_db(
                test_data=test_dataset["Python"],
                db_model=self.RelatedDataLatestModel,
                unique_together_fields=self.unique_together_fields_latest,
            )

            response = self.client.get(self.endpoint_url_latest)
            assert response.status_code == 200

            expected_jsonable = test_dataset["JSONable"]
            actual_jsonable = response.json()
            assert expected_jsonable == actual_jsonable
