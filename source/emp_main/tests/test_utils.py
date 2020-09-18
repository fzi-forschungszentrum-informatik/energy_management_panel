from datetime import datetime, timezone

from django.test import TestCase

from ..utils import datetime_from_timestamp

class TestDatetimeFromTimestamp(TestCase):

    def test_datetime_value_correct(self):
        timestamp = 1596240000000
        expected_datetime = datetime(2020, 8, 1)

        actual_datetime = datetime_from_timestamp(timestamp, tz_aware=False)
        self.assertEqual(expected_datetime, actual_datetime)

    def test_datetime_value_with_tz_correct(self):
        timestamp = 1596240000000
        expected_datetime = datetime(2020, 8, 1)
        expected_datetime = expected_datetime.astimezone(timezone.utc)

        actual_datetime = datetime_from_timestamp(timestamp, tz_aware=True)

        self.assertEqual(expected_datetime, actual_datetime)