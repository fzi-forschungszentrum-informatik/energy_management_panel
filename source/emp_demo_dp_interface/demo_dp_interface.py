import logging
from time import sleep
from random import random
from multiprocessing import Process
from datetime import datetime, timezone

logger = logging.getLogger(__name__)



class DemoDPInterface():
    """
    This is a demo version of a datapoint interface which pushes dummy values
    and metadata into the DB to support the EMP Demo UI App.
    """

    def __new__(cls, *args, **kwargs):
        """
        Ensure singleton, i.e. only one instance is created.
        """
        if not hasattr(cls, "_instance"):
            # This magically calls __init__ with the correct arguements too.
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Spin off a process to simulate asynchronous arrival of data.
        """
        # Logging useful information about the background workers seems to be
        # a good idea, even it is only a debug message.
        logger.info("Starting DemoDPInterface.")

        # Use a process here as it is easier to kill then a thread.
        # The daemon flag is required to prevent the autoreloader to
        # freeze while developing.
        self.worker = Process(target=self.push_data, daemon=True)
        self.worker.start()

    def __del__(self):
        """
        Quit the process once the instance of this class is destroyed.
        """
        if hasattr(self, "worker"):
            self.worker.kill()
            del self.worker

    @staticmethod
    def push_data():
        # Give the remaining components some time to spin up.
        sleep(15)

        # This can only be loaded once all apps are initialized.
        from emp_main.models import Datapoint


        while True:
            # Generate a random value in the range of a typical temperature
            value = round(22 + random() * 3, 1)
            timestamp_as_dt = datetime.utcnow().astimezone(timezone.utc)

            # Updateing/Inserting metadata for a datapoint could look like this:
            dp, created = Datapoint.objects.get_or_create(
                external_id=1,
                type="sensor"
            )
            dp.data_format = "continuous_numeric"
            dp.description = "A dummy temperature like datapoint."
            dp.min_value = 19.0
            dp.max_value = 25.0
            dp.unit = "°C"
            dp.save()

            # Updateing the value for an existing datapoint could look like:
            dp = Datapoint.objects.get(external_id=1)
            dp.last_value = value
            dp.last_value_timestamp = timestamp_as_dt
            dp.save()

            try:
                sleep(30)
            except KeyboardInterrupt:
                # Don't print the process traceback on KeyboardInterrupt
                pass
