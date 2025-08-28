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

    calories_burned = models.FloatField(null=True, blank=True, help_text="Automatic calculated")
    duration_in_minutes = models.FloatField(null=True, blank=True, help_text="Duration in minutes")

    def __str__(self):
        return self.title + " - " + str(self.start)

    @transaction.atomic
    def end_session(self):
        self.duration_in_minutes = self.calculate_current_duration_in_minutes(self.start)
        self.calories_burned = self.calculate_calories()
        self.is_active = False
        self.delete_all_hrr_for_ended_session()
        self.save()

    def delete_all_hrr_for_ended_session(self):
        # Brišemo sve povezane zapise iz baze u jednom pozivu
        self.heart_rate_records.all().delete()

    @classmethod
    def start_session(cls, **kwargs):
        return TrainingSession.objects.create(**kwargs)

    def calculate_calories(self):
        list_of_bpms = [record.bpm for record in self.heart_rate_records.all()]
        print(list_of_bpms, "LIST OF BPMS")
        if len(list_of_bpms) != 0:
            average_bpm = self.calculate_average_heart_rate(list_of_bpms)

            weight = self.client.weight
            age = self.client.user.get_age_from_birth_date()
            duration_in_minutes = self.calculate_current_duration_in_minutes(self.start)
            print(duration_in_minutes, "DURATION AT END")

            if self.client.gender == 'Male':
                calories = ((-55.0969 + (0.6309 * average_bpm) + (0.1988 * weight) + (0.2017 * age)) / 4.184) * duration_in_minutes
            else:
                calories = ((-20.4022 + (0.4472 * average_bpm) - (0.1263 * weight) + (0.074 * age)) / 4.184) * duration_in_minutes

            print(max(round(calories, 2), 0), "CALORIES")
            return max(round(calories, 2), 0)

    def calculate_average_heart_rate(self, list_of_bpms):
        average = sum(list_of_bpms) / len(list_of_bpms)
        return average

    def calculate_current_duration_in_minutes(self, start):
        end = timezone.now()
        duration = (end - start).total_seconds() / 60
        return duration

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
