import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from user.factories import CoachFactory
from user.models.client import Client

User = get_user_model()


@pytest.mark.django_db
class TestUser:
    ####################################################################################################
    # Test user query sets
    ####################################################################################################
    def test_create_client_user_success(self):
        user = User.objects.create_client_user(
            first_name="Miha",
            last_name="Maric",
            email="miha@example.com",
        )

        assert user.email == "miha@example.com"
        assert user.first_name == "Miha"
        assert user.last_name == "Maric"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert User.objects.count() == 1

    def test_create_client_user_without_email_raises_error(self):
        with pytest.raises(ValueError, match="You have not provided a valid e-mail address"):
            User.objects.create_client_user(first_name="Ana", last_name="Petrovic")


@pytest.mark.django_db
class TestClient:
    ####################################################################################################
    # Test client functions
    ####################################################################################################
    def test_create_success(self, tenant):
        coach = CoachFactory(gym=tenant)
        print(coach.user, "COACH USER")
        user_data = {
            "email": "mika@example.com",
            "first_name": "Mika",
            "last_name": "Maric",
        }
        client_data = {
            "gender": "Male",
            "weight": 82.5,
            "height": 180.0,
            "max_heart_rate": 190,
        }

        client = Client.create(user_data=user_data, client_data=client_data, coach=coach)
        print(User.objects.all(), "USERSSSS")

        assert client.pk is not None
        assert client.user.email == "mika@example.com"
        assert client.coach == coach
        assert client.gym == coach.gym  # created via coach.gym in your method
        assert client.gender == "Male"
        # It is 2 because of coach factory
        assert User.objects.count() == 2
        assert Client.objects.count() == 1

    def test_duplicate_user_email_rolls_back_and_raises_validation_error(self, tenant):
        coach = CoachFactory(gym=tenant)

        existing_email = "dup@example.com"
        User.objects.create_client_user(
            email=existing_email, first_name="Ana", last_name="Petrovic"
        )

        user_data = {
            "email": existing_email,
            "first_name": "Nikola",
            "last_name": "Jovanovic",
        }
        client_data = {"gender": "Female"}

        with pytest.raises(ValidationError) as exc:
            Client.create(user_data=user_data, client_data=client_data, coach=coach)

        assert "detail" in exc.value.message_dict

        # Atomic rollback: no new client should have been created
        assert Client.objects.count() == 0

        # User count still 1 (the pre-existing one); no partial user leftover from failed create
        assert User.objects.filter(email=existing_email).count() == 1
