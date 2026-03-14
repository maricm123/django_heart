from django.db import models
from core.models.behaviours import TimeStampable
from gym.models.gym_tenant import GymTenant


class GymParameters(TimeStampable):
    gym = models.OneToOneField(
        GymTenant,
        on_delete=models.CASCADE,
        related_name='parameters'
    )

    class Meta:
        verbose_name_plural = "Gym Parameters"

    def __str__(self):
        return f"Parameters for {self.gym.name}"
