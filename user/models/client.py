from django.db import models
from user.models.base_profile import BaseProfile
from user.models.coach import Coach
from django.contrib.auth import get_user_model

User = get_user_model()


class Client(BaseProfile):
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

    def __str__(self):
        return self.user.name
