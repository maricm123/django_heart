from training_session.exceptions import CannotDeleteActiveTrainingSessionError
from training_session.selectors import training_session_per_client_list_data
from training_session.services import get_client_max_heart_rate
from training_session.tests.factories import TrainingSessionFactory
import pytest
from django.utils import timezone
from datetime import date
from user.tests.factories import ClientFactory, UserFactory


@pytest.mark.django_db
class TestTrainingSession:

    def test_selector_training_session_per_client_test(self, session_env):
        tenant = session_env["tenant"]
        coach = session_env["coach"]
        client = session_env["client"]
        client2 = session_env["client2"]

        TrainingSessionFactory(
            client=client,
            gym=tenant,
            coach=coach,
            is_active=False,
            start=timezone.now()
        )
        TrainingSessionFactory(
            client=client,
            gym=tenant,
            coach=coach,
            is_active=True,
            start=timezone.now()
        )
        TrainingSessionFactory(
            client=client2,
            gym=tenant,
            coach=coach,
            is_active=False,
            start=timezone.now()
        )

        result = training_session_per_client_list_data(client.id)
        assert len(result) == 1

    def test_delete_training_session_function(self, session_env):
        tenant = session_env["tenant"]
        coach = session_env["coach"]
        client = session_env["client"]

        session = TrainingSessionFactory(
            client=client, gym=tenant, coach=coach, is_active=False, deleted_at=None, start=timezone.now()
        )

        session.delete()

        assert session.deleted_at is not None

    def test_raise_error_when_delete_active_training_session(self, session_env):
        tenant = session_env["tenant"]
        coach = session_env["coach"]
        client2 = session_env["client2"]

        session = TrainingSessionFactory(
            client=client2, gym=tenant, coach=coach, is_active=True, deleted_at=None, start=timezone.now()
        )

        with pytest.raises(CannotDeleteActiveTrainingSessionError):
            session.delete()

    def test_force_delete_training_session_function(self, session_env):
        tenant = session_env["tenant"]
        coach = session_env["coach"]
        client = session_env["client"]

        session = TrainingSessionFactory(
            client=client, gym=tenant, coach=coach, is_active=True, deleted_at=None, start=timezone.now()
        )

        session.force_delete_active_training_session()

        assert session.deleted_at is not None
        assert session.is_active is False

    def test_get_client_max_heart_rate_from_database(self, session_env):
        tenant = session_env["tenant"]
        coach = session_env["coach"]
        user = UserFactory(
            birth_date=date(2010, 0o7, 18)
        )
        client2 = ClientFactory(
            user=user,
            coach=coach,
            gym=tenant,
            max_heart_rate=200
        )

        samples = [
            ("2025-01-10T10:00:00Z", 91),
            ("2025-01-10T10:01:00Z", 92),
            ("2025-01-10T10:02:00Z", 95),
            ("2025-01-10T10:03:00Z", 94),
            ("2025-01-10T10:04:00Z", 97),
        ]

        max_hr = get_client_max_heart_rate(client2, samples)

        assert max_hr == client2.max_heart_rate
        assert max_hr != client2.user.age

    def test_get_client_max_heart_rate_from_session(self, session_env):
        tenant = session_env["tenant"]
        coach = session_env["coach"]
        user = UserFactory(
            birth_date=date(2010, 0o7, 18)
        )
        client2 = ClientFactory(
            user=user,
            coach=coach,
            gym=tenant,
            max_heart_rate=190
        )

        samples = [
            ("2025-01-10T10:00:00Z", 199),
            ("2025-01-10T10:01:00Z", 92),
            ("2025-01-10T10:02:00Z", 95),
            ("2025-01-10T10:03:00Z", 94),
            ("2025-01-10T10:04:00Z", 97),
        ]

        max_hr = get_client_max_heart_rate(client2, samples)

        assert max_hr == 199
        # Make sure it is updated in database
        assert max_hr == client2.max_heart_rate
        assert max_hr != client2.user.age

    def test_get_client_max_heart_rate_not_update(self, session_env):
        tenant = session_env["tenant"]
        coach = session_env["coach"]
        user = UserFactory(
            birth_date=date(2010, 0o7, 18)
        )
        client2 = ClientFactory(
            user=user,
            coach=coach,
            gym=tenant,
            max_heart_rate=None
        )

        samples = [
            ("2025-01-10T10:00:00Z", 120),
            ("2025-01-10T10:01:00Z", 92),
            ("2025-01-10T10:02:00Z", 95),
            ("2025-01-10T10:03:00Z", 94),
            ("2025-01-10T10:04:00Z", 97),
        ]

        max_hr = get_client_max_heart_rate(client2, samples)
        assert max_hr is None
        assert client2.max_heart_rate is None
