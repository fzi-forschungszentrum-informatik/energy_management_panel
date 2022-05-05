import os
from datetime import datetime, timezone
import logging
from random import random
from time import sleep

from esg.api_client.emp import EmpClient
from esg.models.datapoint import DatapointList
from esg.models.datapoint import ValueMessageByDatapointId

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s"
)
logger = logging.getLogger(__name__)


class DemoDPInterface:
    """
    This is a demo version of a datapoint interface which pushes dummy values
    and metadata into the DB to support the EMP Demo UI App.
    """

    def __init__(self,):
        """
        Configure datapoint interface.
        """
        logger.info("Starting up DemoDPInterface")
        # Give the EMP some time to boot.
        sleep(15)

        self.api_url = os.getenv("EMP_API_URL")
        self.emp_client = EmpClient(base_url=self.api_url)

        logger.info("Testing connection to EMP API at {}".format(self.api_url))
        self.emp_client.test_connection()

    def update_datapoints(self):
        """
        Usually one would fetch the datapoint metadata from some source
        but for the demo we simply define it here.
        """
        # Define the metadata of a datapoint.
        datapoint = {
            "origin": "DemoDPInterface",
            "origin_id": "42",
            "short_name": "T_dummy",
            "type": "Sensor",
            "data_format": "Continuous Numeric",
            "description": "A dummy temperature like datapoint.",
            "allowed_values": None,
            # This could be the measurement range of the sensor.
            "min_value": 0.0,
            "max_value": 50.0,
            "unit": "°C",
        }

        # API expects a list of datapoints.
        datapoint_list = DatapointList.parse_obj({"__root__": [datapoint]})

        # Push to EMP, this returns the datapoint metadata as confirmation
        # sorted by datapoint IDs.
        datapoints_by_id = self.emp_client.put_datapoint_metadata_latest(
            datapoint_list=datapoint_list
        )

        logger.info("Pushed datapoint metadata to EMP.")

        # Make a map between internal EMP IDs and EMP IDs.
        self.datapoint_id_map = {}
        for emp_id in datapoints_by_id.__root__:
            datapoint_obj = datapoints_by_id.__root__[emp_id]
            self.datapoint_id_map[datapoint_obj.origin_id] = emp_id

        logger.info(
            "Created datapoint ID map: {}".format(self.datapoint_id_map)
        )

    def update_values(self):
        """
        Usually measured values would be received from some device or
        hardware abstraction component. Here we just compute a random
        value on every call to simulate activity.
        """

        value_msg_internal_id = "42"
        value_message = {
            "value": round(22 + random() * 3, 1),
            "time": datetime.utcnow().astimezone(timezone.utc),
        }

        # get EMP ID if the corresponding datapoint.
        emp_id = self.datapoint_id_map[value_msg_internal_id]

        # use construct_recursive only if you are sure that the values
        # are correct and match the message format.
        value_msgs_by_dp_id = ValueMessageByDatapointId.construct_recursive(
            __root__={emp_id: value_message}
        )

        # Push to EMP.
        put_summary = self.emp_client.put_datapoint_value_latest(
            value_msgs_by_dp_id=value_msgs_by_dp_id
        )

        logger.info(
            "Put value messages latest: {} updated, {} created."
            "".format(put_summary.objects_updated, put_summary.objects_created)
        )

    def main(self):
        """
        Main loop. Here we know that datapoint metadata doesn't change,
        hence there is no point in updating more then once.
        Beyond that we simulate that a value message is received every
        five seconds.
        """
        self.update_datapoints()

        while True:
            self.update_values()
            sleep(5)


if __name__ == "__main__":
    demp_dp_interface = DemoDPInterface()
    demp_dp_interface.main()
