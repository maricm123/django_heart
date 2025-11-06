from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError
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
    weight = models.FloatField(null=True, blank=True)  # KG
    height = models.FloatField(null=True, blank=True)

    max_heart_rate = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.name

    @classmethod
    def create(cls, user_data: dict, client_data: dict, coach):
        with transaction.atomic():
            try:
                user = User.objects.create_client_user(**user_data)
                client = cls.objects.create(user=user, coach=coach, gym=coach.gym, **client_data)
            except (IntegrityError, ValidationError) as e:
                raise ValidationError({"detail": "Client with this user already exists."}, e)
        return client

    @property
    def sessions_this_month(self):
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        return self.sessions.filter(
            start__gte=start_of_month,
            start__lte=now
        )
