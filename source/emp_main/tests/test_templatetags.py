from django.test import TestCase, Client

from ..models import Datapoint
from ..templatetags.datapoint_helpers import dp_field_value

class TestDpFieldValue(TestCase):

    @classmethod
    def setUpTestData(cls):
        default_field_values = {"type": "sensor"}
        cls.dp = Datapoint.objects.create(**default_field_values)
        cls.dp.save()

    def test_error_returned_for_not_existing_field_name(self):
        """
        Ensure that an error message is returned for not existing fields.
        """
        expected_error = "Error! Datapoint has no field name \"na_bbbb\""
        actual_return = dp_field_value(self.dp, "na_bbbb")
        self.assertIn(expected_error, actual_return)

    def test_returned_html_with_span_tag_and_class_label(self):
        expected_class_label = '"dp%s__type"' % self.dp.id
        expected_html = "<span class=%s>sensor</span>" % expected_class_label
        actual_html = dp_field_value(self.dp, "type")
        self.assertEqual(expected_html, actual_html)
