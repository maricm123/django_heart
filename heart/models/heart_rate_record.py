from django.db import models
from django.contrib.auth import get_user_model
from training_session.models import TrainingSession
User = get_user_model()


class HeartRateRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
        return self.user + " " + self.device_id
