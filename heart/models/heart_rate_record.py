from django.db import models
from training_session.models import TrainingSession
from user.models import Client


class HeartRateRecord(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=100)
    # add later , this reduces storage and makes joins cleaner
    # device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True)
    bpm = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)  # timestamp from server
    session_timestamp = models.DateTimeField(blank=True, null=True)  # actual beat time (or equal to timestamp by default)

    training_session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='heart_rate_records'
    )

    class Meta:
        #  because aggregation will query training session per timestamp
        indexes = [
            models.Index(fields=['training_session', 'timestamp']),
        ]

    def __str__(self):
        return str(self.client) + " " + str(self.device_id)
