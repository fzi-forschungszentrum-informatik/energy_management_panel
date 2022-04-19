import logging
from time import sleep
from random import random
from threading import Thread
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
        else:
            logger.warning(
                "ConnectorMQTTIntegration is aldready running. Use "
                "get_instance method to retrieve the running instance."
            )
        return cls._instance

    @classmethod
    def get_instance(cls):
        """
        Return the running instance of the class.

        Returns:
        --------
        instance: EMPAppsCache instance
            The running instance of the class. Is none of not running yet.
        """
        if hasattr(cls, "_instance"):
            instance = cls._instance
        else:
            instance = None
        return instance

    def __init__(self):
        """
        Spin off a thread to simulate asynchronous arrival of data.
        """
        # This will be called twice on "./manage.py runserver" by django.
        # At the first time we wish to run this function, the second time not.
        if not hasattr(self, "_is_initialized"):
            # Logging useful information about the background workers seems to
            # be a good idea, even it is only a debug message.
            logger.info("Starting DemoDPInterface.")

            # This must be a thread as the save method of Datapoint spawns a
            # signal. This signal is only received if sender and
            # receiver live in the same process.
            self.thread = Thread(target=self.push_data)
            # Don't wait on this thread on shutdown.
            self.thread.daemon = True
            self.thread.start()

            self._is_initialized = True

    def push_data(self):
        """
        Push fake values to Datapoint in DB for demo purposes.
        """
        # Give the remaining components some time to spin up.
        sleep(10)

        # This can only be loaded once all apps are initialized.
        from emp_main.models import Datapoint

        # Updateing/Inserting metadata for a datapoint could look like this:
        dp, created = Datapoint.objects.get_or_create(
            origin_id=1,
            type="sensor"
        )
        dp.data_format = "continuous_numeric"
        dp.description = "A dummy temperature like datapoint."
        dp.min_value = 19.0
        dp.max_value = 25.0
        dp.unit = "°C"
        dp.save()

        while True:
            # Generate a random value in the range of a typical temperature
            value = round(22 + random() * 3, 1)
            timestamp_as_dt = datetime.utcnow().astimezone(timezone.utc)

            # Updateing the value for an existing datapoint could look like
            # this. Specifingy update_fields is good practice and allows
            # methods listening to the save signals to determine if relevant
            # information has been updated.
            # Please ensure that the new values match the fields. E.g.
            # last_value is string field but will also accept a number. However
            # the methods listening to post_save (e.g. consumers notifing the
            # user about new data) will expect a string.
            dp = Datapoint.objects.get(origin_id=1)
            dp.last_value = str(value)
            dp.last_value_timestamp = timestamp_as_dt
            dp.save(update_fields=["last_value", "last_value_timestamp"])

            sleep(5)
