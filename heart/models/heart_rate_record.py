from django.db import models
from training_session.models import TrainingSession
from user.models import Client


class HeartRateRecord(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=100)
    bpm = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    training_session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='heart_rate_records'
    )

    def __str__(self):
        return str(self.client) + " " + str(self.device_id)
