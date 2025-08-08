from django.db import models

from user.models.base_profile import BaseProfile
from user.models.coach import Coach


class Client(BaseProfile):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)

    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female")],
        null=True,
        blank=True
    )
    weight = models.FloatField(null=True, blank=True)  # KG
    height = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name
