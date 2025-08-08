from django.db import models
from user.models.base_profile import BaseProfile


class Coach(BaseProfile):
    specialty = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
