from django.db import models

from emp_main.models import Datapoint


class DatapointValue(models.Model):

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=(
            "The datapoint that the value message belongs to."
        )
    )
    value = models.TextField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The value field in datapoint value msg."
        )
    )
    timestamp = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The field that stores the timestamp of value msg as datetime."
        )
    )

    def save(self, *args, **kwargs):
        """
        Update the last_value/last_value_timestamp fields in datapoint too.
        """
        # But check first that the save for this object goes trough.
        super().save(*args, **kwargs)

        # A message without a timestamp cannot be latest.
        if self.timestamp is None:
            return

        self.datapoint.refresh_from_db()
        existing_ts = self.datapoint.last_value_timestamp

        if existing_ts is None or existing_ts <= self.timestamp:
            self.datapoint.last_value = self.value
            self.datapoint.last_value_timestamp = self.timestamp
            self.datapoint.save()

class DatapointSchedule(models.Model):

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=(
            "The datapoint that the schedule message belongs to."
        )
    )
    schedule = models.JSONField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The schedule field in datapoint schedule msg."
        )
    )
    timestamp = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The field that stores the timestamp of schedule msg as datetime."
        )
    )

    def save(self, *args, **kwargs):
        """
        Update the last_schedule/last_schedule_timestamp fields in datapoint
        too.
        """
        # But check first that the save for this object goes trough.
        super().save(*args, **kwargs)

        # A message without a timestamp cannot be latest.
        if self.timestamp is None:
            return

        self.datapoint.refresh_from_db()
        existing_ts = self.datapoint.last_schedule_timestamp

        if existing_ts is None or existing_ts <= self.timestamp:
            self.datapoint.last_schedule = self.schedule
            self.datapoint.last_schedule_timestamp = self.timestamp
            self.datapoint.save()

class DatapointSetpoint(models.Model):

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete=models.CASCADE,
        help_text=(
            "The datapoint that the setpoint message belongs to."
        )
    )
    setpoint = models.JSONField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The setpoint field in datapoint setpoint msg."
        )
    )
    timestamp = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text=(
            "The field that stores the timestamp of setpoint msg as datetime."
        )
    )
    
    def save(self, *args, **kwargs):
        """
        Update the last_setpoint/last_setpoint_timestamp fields in datapoint
        too.
        """
        # But check first that the save for this object goes trough.
        super().save(*args, **kwargs)

        # A message without a timestamp cannot be latest.
        if self.timestamp is None:
            return

        self.datapoint.refresh_from_db()
        existing_ts = self.datapoint.last_setpoint_timestamp

        if existing_ts is None or existing_ts <= self.timestamp:
            self.datapoint.last_setpoint = self.setpoint
            self.datapoint.last_setpoint_timestamp = self.timestamp
            self.datapoint.save()
