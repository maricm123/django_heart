from django.db import models

from core.models.behaviours import DeletedAt
from user.exceptions import CannotDeleteClientWhileInActiveTrainingSession
from user.models.base_profile import BaseProfile
from user.models.coach import Coach
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            deleted_at__isnull=True
        )


class Client(
    BaseProfile,
    DeletedAt
):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)

    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
        null=True,
        blank=True
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Weight in kilograms (kg)"
    )

    height = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Height in centimeters (cm)"
    )

    max_heart_rate = models.PositiveIntegerField(null=True, blank=True)
    auto_calculate_max_hr = models.BooleanField(
        help_text="Coach choose an option, will max heart rate being calculated based on client age",
        default=False,
        null=False,
        blank=False
    )

    objects = ActiveManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.user.name

    @property
    def has_active_sessions(self):
        return self.sessions.filter(is_active=True).exists()

    @property
    def name(self):
        return self.user.first_name + " " + self.user.last_name

    # Write test for this
    @property
    def max_heart_rate_value(self):
        """
        Returns the client's max heart rate:
        1. If max_heart_rate is set, use it.
        2. If not, and auto_calculate_max_hr is True, calculate as 220 - age.
        3. Otherwise, return None.
        """
        if self.max_heart_rate:
            return self.max_heart_rate

        if self.auto_calculate_max_hr and self.user and self.user.age:
            return 220 - self.user.age

        return None

    def delete(self, using=None, keep_parents=False):
        if self.has_active_sessions:
            raise CannotDeleteClientWhileInActiveTrainingSession

        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

        if self.user:
            self.user.is_active = False
            self.user.save(update_fields=["is_active"])
