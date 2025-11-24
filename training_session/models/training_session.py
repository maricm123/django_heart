from django.db import models
from core.models.behaviours import TimeStampable, DateTimeFramable, IsActive, DeletedAt
from django.contrib.auth import get_user_model
from gym.models import GymTenant
from training_session.exceptions import CannotDeleteActiveTrainingSessionError
from user.models.client import Client
from user.models.coach import Coach
from django.utils import timezone

User = get_user_model()


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            deleted_at__isnull=True
        )


class TrainingSession(
    TimeStampable,
    DateTimeFramable,
    IsActive,
    DeletedAt
):
    title = models.CharField(max_length=255, null=False, blank=False)

    gym = models.ForeignKey(
        GymTenant,
        on_delete=models.CASCADE,
        related_name="training_sessions"
    )
    coach = models.ForeignKey(
        Coach,
        null=True,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    client = models.ForeignKey(
        Client,
        null=True,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    calories_burned = models.DecimalField(
        null=True,
        blank=True,
        help_text="Automatic calculated",
        decimal_places=2,
        max_digits=8
    )
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in seconds")

    # Derived summary metrics (cached result for fast UI reads)
    summary_metrics = models.JSONField(default=dict, blank=True)
    """
    {
      "id": 11,
      "start_time": "2025-02-01T10:00:00Z",
      "summary_metrics": {
        "avg_hr": 142,
        "max_hr": 189,
        "duration_seconds": 2900,
        "calories": 395,
        "hr_zones": {
          "z1_minutes": 5,
          "z2_minutes": 12,
          "z3_minutes": 18,
          "z4_minutes": 9,
          "z5_minutes": 3
        }
      },
      "chart_points": [
        { "timestamp": "2025-02-01T10:00:00Z", "bpm": 120 },
        { "timestamp": "2025-02-01T10:00:10Z", "bpm": 128 },
        { "timestamp": "2025-02-01T10:00:20Z", "bpm": 131 }
      ]
    }
    """

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        if self.coach:
            return self.title + " - " + str(self.start) + " - " + str(self.coach.user.name)
        return self.title + " - " + str(self.start)

    @classmethod
    def start_training_session(cls, **kwargs):
        return TrainingSession.objects.create(**kwargs)

    def delete(self, using=None, keep_parents=False):
        if self.is_active:
            raise CannotDeleteActiveTrainingSessionError
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
