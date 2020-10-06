import json
from html import unescape
from django.test import TestCase

from ..models import Datapoint
from ..templatetags.datapoint_helpers import dp_field_value, dp_update_map

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
        expected_error = "Error! Datapoint has no field name"
        actual_return = dp_field_value(self.dp, "na_bbbb")
        self.assertIn(expected_error, actual_return)

    def test_returned_html_with_span_tag_and_class_label(self):
        expected_class_label = 'dp%s__type' % self.dp.id
        expected_html = "<span class=%s>sensor</span>" % expected_class_label
        actual_html = dp_field_value(self.dp, "type")
        self.assertEqual(expected_html, actual_html)

    def test_datapoint_id_in_new_field_connector(self):
        """
        If used, the field_collector should store the ids of all datapoints
        for which fields have been used. This allows us to request updates
        for these fields.
        """
        field_collector = {}
        _ = dp_field_value(self.dp, "type", field_collector)
        self.assertIn(self.dp.id, field_collector)

    def test_class_label_in_new_field_connector(self):
        """
        If used, the field_collector should store the class labels of
        all the fields that have been used. This allows us to request updates
        for these fields.
        """
        field_collector = {}
        _ = dp_field_value(self.dp, "type", field_collector)

        expected_class_label = 'dp%s__type' % self.dp.id
        self.assertIn(expected_class_label, field_collector[self.dp.id])

    def test_class_label_in_existing_field_connector(self):
        """
        If used, the field_collector should store the class labels of
        all the fields that have been used. This allows us to request updates
        for these fields.
        """
        field_collector = {}
        _ = dp_field_value(self.dp, "type", field_collector)
        _ = dp_field_value(self.dp, "last_value", field_collector)

        expected_class_label_1 = 'dp%s__type' % self.dp.id
        expected_class_label_2 = 'dp%s__last_value' % self.dp.id

        self.assertIn(expected_class_label_1, field_collector[self.dp.id])
        self.assertIn(expected_class_label_2, field_collector[self.dp.id])


class TestDpUpdateMap(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_field_collector = {
            1: set(["dp1__type", "dp1__last_value"]),
            2: set(["dp2__type", "dp2__last_value"]),
        }

    def test_datapoint_ids_in_json_output(self):
        """
        Verify that the datapoint ids are also in the keys in the json output.
        """
        actual_update_map = dp_update_map(self.test_field_collector, False)

        # Parse actual_update_map as we don not enforce ordering in JSON
        # and check that the expected content is in there.
        parsed_update_map = json.loads(unescape(actual_update_map))
        for expected_datapoint_id in self.test_field_collector:
            # JSON keys are always strings
            expected_datapoint_id = str(expected_datapoint_id)

            self.assertIn(expected_datapoint_id, parsed_update_map.keys())

        # Verify we got no extra datapoint ids.
        self.assertEquals(
            len(self.test_field_collector.keys()),
            len(parsed_update_map)
        )

    def test_datapoint_class_labels_in_json_output(self):
        """
        Verify that the datapoint class labels are also in the json output.
        """
        actual_update_map = dp_update_map(self.test_field_collector, False)

        # Parse actual_update_map as we don not enforce ordering in JSON
        # and check that the expected content is in there.
        parsed_update_map = json.loads(unescape(actual_update_map))
        for test_datapoint_id in self.test_field_collector:
            # JSON keys are always strings
            expected_datapoint_id = str(test_datapoint_id)

            ecls = self.test_field_collector[test_datapoint_id]
            actual_class_labels = parsed_update_map[expected_datapoint_id]
            for expected_class_label in ecls:
                self.assertIn(expected_class_label, actual_class_labels)
