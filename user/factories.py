import factory
from django.utils import timezone
from django.contrib.auth import get_user_model
from phonenumber_field.phonenumber import PhoneNumber
# from conftest import gym_public
from gym.models import GymTenant
from user.models.coach import Coach
from user.models.client import Client

User = get_user_model()


class GymFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GymTenant

    name = factory.Sequence(lambda n: f"Gym {n}")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        from django_tenants.utils import schema_context
        with schema_context("public"):
            return super()._create(model_class, *args, **kwargs)


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating User instances for tests.
    Example:
        user = UserFactory()
        admin = UserFactory(is_superuser=True, is_staff=True)
        inactive_user = UserFactory(is_active=False)
    """

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_superuser = False
    is_staff = False
    date_joined = factory.LazyFunction(timezone.now)

    profile_image_url = factory.Faker("image_url")
    birth_date = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)
    phone_number = factory.LazyFunction(lambda: PhoneNumber.from_string("+381641234567"))

    class Meta:
        model = User
        django_get_or_create = ("email",)


class CoachFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Coach  # adjust to your real model

    user = factory.SubFactory(UserFactory)
    gym = factory.SubFactory(GymFactory)
    specialty = None


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    user = factory.SubFactory(UserFactory)
    coach = factory.SubFactory(CoachFactory)
    # Optional fields
    gender = None
    weight = None
    height = None
    max_heart_rate = None
