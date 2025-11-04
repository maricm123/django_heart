import factory
from django.utils import timezone
from django.contrib.auth import get_user_model
from phonenumber_field.phonenumber import PhoneNumber

User = get_user_model()


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
