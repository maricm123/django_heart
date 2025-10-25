from django.db import models, transaction
from core.models.behaviours import TimeStampable, DateTimeFramable, IsActive
from django.contrib.auth import get_user_model
from gym.models import GymTenant
from user.models.client import Client
from user.models.coach import Coach
from django.utils import timezone
User = get_user_model()


class TrainingSession(
    TimeStampable,
    DateTimeFramable,
    IsActive
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

    def __str__(self):
        if self.coach:
            return self.title + " - " + str(self.start) + " - " + str(self.coach.user.name)
        return self.title + " - " + str(self.start)

    @transaction.atomic
    def end_session(self, calories_at_end, duration):
        self.duration = duration
        self.calories_burned = calories_at_end
        self.is_active = False
        self.end = timezone.now()
        self.delete_all_hrr_for_ended_session()
        self.save()

    def delete_all_hrr_for_ended_session(self):
        # Brišemo sve povezane zapise iz baze u jednom pozivu
        self.heart_rate_records.all().delete()

    @classmethod
    def start_session(cls, **kwargs):
        return TrainingSession.objects.create(**kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def calculate_current_duration_in_minutes(self, start):
        end = timezone.now()
        duration = (end - start).total_seconds() / 60
        return duration
