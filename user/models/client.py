from django.db import models, IntegrityError
from django.db import models, transaction
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

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
        return self.user.name

    @classmethod
    def create(cls, user_data: dict, client_data: dict, coach):
        """Atomic create of user + client"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        with transaction.atomic():
            try:
                user = User.objects.create_user(**user_data)
                client = cls.objects.create(user=user, coach=coach, gym=coach.gym, **client_data)
            except IntegrityError as e:
                # Clean rollback is automatic
                raise ValidationError({"detail": "Client with this user already exists."})
        return client
