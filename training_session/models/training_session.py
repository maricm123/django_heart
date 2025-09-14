from django.db import models, transaction
from apis.utils_for_calculating_calories import (
    calculate_current_duration_in_minutes,
)
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

    calories_burned = models.FloatField(null=True, blank=True, help_text="Automatic calculated")
    duration_in_minutes = models.FloatField(null=True, blank=True, help_text="Duration in minutes")

    def __str__(self):
        return self.title + " - " + str(self.start)

    @transaction.atomic
    def end_session(self, calories_at_end):
        self.duration_in_minutes = self.calculate_current_duration_in_minutes(self.start)
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
