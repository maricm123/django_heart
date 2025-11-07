from user.models import Client
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


@transaction.atomic()
def client_create(user_data: dict, client_data: dict, coach):
    try:
        user = User.objects.create_client_user(**user_data)
        client = Client.objects.create(user=user, coach=coach, gym=coach.gym, **client_data)
    except (IntegrityError, ValidationError) as e:
        raise ValidationError({"detail": "Client with this user already exists."}, e)
    return client
