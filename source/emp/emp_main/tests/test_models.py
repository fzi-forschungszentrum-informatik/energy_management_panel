from copy import deepcopy

from django.test import TestCase
from django.db.utils import IntegrityError
from esg.test.django import GenericDjangoModelTestMixin
from esg.test import data as td

from ..models import Datapoint as DatapointDb
from ..models import Plant as PlantDb


class TestDatapoint(TestCase, GenericDjangoModelTestMixin):
    Datapoint = DatapointDb
    model_name = "Datapoint"
    msgs_as_python = [m["Python"] for m in td.datapoints]
    msgs_as_jsonable = [m["JSONable"] for m in td.datapoints]
    invalid_msgs_as_python = []

    # This is specific for this test class.
    default_field_values = {"type": "sensor"}

    def prepare_messages(self, msgs, msg_name):
        """
        Add foreign keys to positions.
        """
        msgs = deepcopy(msgs)
        for i, msg in enumerate(msgs):
            msg["id"] = i
        return msgs

    def generic_field_value_test(self, field_values):
        """
        Create a datapoint with field_values, and check that the value can be
        restored.
        """
        datapoint = self.Datapoint.objects.create(**field_values)
        datapoint.save()
        # Ensure that we compare to the value that has been stored in DB.
        datapoint.refresh_from_db()
        for field in field_values:
            expected_value = field_values[field]
            actual_value = getattr(datapoint, field)
            self.assertEqual(expected_value, actual_value)

    def test_save_replaces_origin_id_with_None(self):
        """
        The admin would save an empty string which is not unique.
        """
        field_values = self.default_field_values.copy()
        field_values.update({"origin_id": ""})

        datapoint = self.Datapoint.objects.create(**field_values)

        self.assertEqual(datapoint.origin_id, None)

    def test_fields_origin_and_origin_id_unique_together(self):
        """
        origin_id must be unique as we use it to select a single datapoint
        which is updated with the data from the external system.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"origin": "test", "origin_id": "1"})

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

    def test_field_short_name_is_not_unique_when_null(self):
        """
        If createad automatically, short_name is null, which should not trigger
        the unique constraint.
        """
        field_values = self.default_field_values.copy()

        field_values.update({"short_name": None})

        self.generic_field_value_test(field_values=field_values)
        self.generic_field_value_test(field_values=field_values)


class TestPlant(TestCase, GenericDjangoModelTestMixin):
    Plant = PlantDb
    model_name = "Plant"
    msgs_as_python = [m["Python"] for m in td.plants]
    msgs_as_jsonable = [m["JSONable"] for m in td.plants]
    invalid_msgs_as_python = [m["Python"] for m in td.invalid_plants]


# class TestGeographicPosition(
#     TestCase, GenericDjangoModelTestMixin
# ):
#
#     model_name = "GeographicPosition"
#     msgs_as_python = [m["Python"] for m in td.geographic_positions]
#     msgs_as_jsonable = [m["JSONable"] for m in td.geographic_positions]
#     invalid_msgs_as_python = [
#         m["Python"] for m in td.invalid_geographic_positions
#     ]
#
#     def prepare_messages(self, msgs):
#         """
#         Add foreign keys to positions.
#         """
#         msgs = deepcopy(msgs)
#         for i, msg in enumerate(msgs):
#             msg["plant"] = self.Plant(name="test_plant_{}".format(i))
#             msg["plant"].save()
#         return msgs
