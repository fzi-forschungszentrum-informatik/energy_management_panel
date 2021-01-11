import json

from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import Datapoint
from ..utils import datetime_from_timestamp

class TestDemoAppPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Generic default values to prevent errors when creating datapoints
        # while violating non empty constraints.
        cls.default_field_values = {"type": "sensor"}


    def generic_field_value_test(self, field_values):
        """
        Create a datapoint with field_values, and check that the value can be
        restored.
        """
        datapoint = Datapoint.objects.create(**field_values)
        datapoint.save()
        # Ensure that we compare to the value that has been stored in DB.
        datapoint.refresh_from_db()
        for field in field_values:
            expected_value = field_values[field]
            actual_value = getattr(datapoint, field)
            self.assertEqual(expected_value, actual_value)

    def test_field_origin_id_exists(self):
        """
        This field is required to match externally managed datapoint metadata.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"origin_id": "1"})

        self.generic_field_value_test(field_values=field_values)

    def test_field_origin_id_is_unique(self):
        """
        origin_id must be unique as we use it to select a single datapoint
        which is updated with the data from the external system.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"origin_id": "1"})

        self.generic_field_value_test(field_values=field_values)
        with self.assertRaises(IntegrityError):
            self.generic_field_value_test(field_values=field_values)

    def test_field_origin_id_is_not_unique_when_null(self):
        """
        Verify that we can have several datapoints with all null as origin_id
        as this will happen if we add additional datapoints locally while others
        exist that are pushed from the external system.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"origin_id": None})

        self.generic_field_value_test(field_values=field_values)
        self.generic_field_value_test(field_values=field_values)

    def test_field_type_exists(self):
        """
        This field is an essential information about the datapoint.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"type": "actuator"})

        self.generic_field_value_test(field_values=field_values)

    def test_field_data_format_exists(self):
        """
        This field is an essential information about the datapoint.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"data_format": "generic_numeric"})

        self.generic_field_value_test(field_values=field_values)

    def test_field_decription_exists(self):
        """
        This field is an essential information about the datapoint.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"description": "Sample text"})

        self.generic_field_value_test(field_values=field_values)

    def test_last_value_exists(self):
        """
        This field stores datapoint payload.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"last_value": "3.12345"})

        self.generic_field_value_test(field_values=field_values)

    def test_last_value_timestamp_exists(self):
        """
        This field stores datapoint payload.
        """
        field_values = self.default_field_values.copy()

        ts = 1596240000000
        ts_datetime = datetime_from_timestamp(ts, tz_aware=True)
        field_values.update({"last_value_timestamp": ts_datetime})

        self.generic_field_value_test(field_values=field_values)


    def test_last_setpoint_exists(self):
        """
        This field stores datapoint payload.

        TODO: Add realistic setpoint.
        """
        field_values = self.default_field_values.copy()

        last_setpoint = json.dumps([
            {
                'from_timestamp': None,
                'to_timestamp': 1564489613491,
                'preferred_value': 21,
            },
            {
                'from_timestamp': 1564489613491,
                'to_timestamp': None,
                'preferred_value': None,
            }
        ])
        field_values.update({"last_setpoint": last_setpoint})

        self.generic_field_value_test(field_values=field_values)

    def test_last_setpoint_timestamp_exists(self):
        """
        This field stores datapoint payload.
        """
        field_values = self.default_field_values.copy()

        ts = 1596240000000
        ts_datetime = datetime_from_timestamp(ts, tz_aware=True)
        field_values.update({"last_setpoint_timestamp": ts_datetime})

        self.generic_field_value_test(field_values=field_values)

    def test_last_schedule_exists(self):
        """
        This field stores datapoint payload.

        TODO: Add realistic schedule.
        """
        field_values = self.default_field_values.copy()

        last_schedule = json.dumps([
            {
                'from_timestamp': None,
                'to_timestamp': 1564489613491,
                'value': 21
            },
            {
                'from_timestamp': 1564489613491,
                'to_timestamp': None,
                'value': None
            }
        ])
        field_values.update({"last_schedule": last_schedule})

        self.generic_field_value_test(field_values=field_values)

    def test_last_schedule_timestamp_exists(self):
        """
        This field stores datapoint payload.
        """
        field_values = self.default_field_values.copy()

        ts = 1596240000000
        ts_datetime = datetime_from_timestamp(ts, tz_aware=True)
        field_values.update({"last_schedule_timestamp": ts_datetime})

        self.generic_field_value_test(field_values=field_values)

    def test_field_allowed_values_exists(self):
        """
        This field carries additional metadata on the datapoint.
        """
        field_values = self.default_field_values.copy()

        allowed_values = json.dumps([1, 2, 3])
        field_values.update({"allowed_values": allowed_values})

        self.generic_field_value_test(field_values=field_values)

    def test_field_min_value_exists(self):
        """
        This field carries additional metadata on the datapoint.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"min_value": 10.0})

        self.generic_field_value_test(field_values=field_values)

    def test_field_max_value_exists(self):
        """
        This field carries additional metadata on the datapoint.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"max_value": 10.0})

        self.generic_field_value_test(field_values=field_values)

    def test_unit_exists(self):
        """
        This field carries additional metadata on the datapoint.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"unit": "Mg*m*s^-2"})

        self.generic_field_value_test(field_values=field_values)
