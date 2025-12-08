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

    def delete(self, using=None, keep_parents=False):
        if self.has_active_sessions:
            raise CannotDeleteClientWhileInActiveTrainingSession

        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

        if self.user:
            self.user.is_active = False
            self.user.save(update_fields=["is_active"])
