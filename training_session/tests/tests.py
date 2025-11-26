from training_session.exceptions import CannotDeleteActiveTrainingSessionError
from training_session.selectors import training_session_per_client_list_data
from training_session.tests.factories import TrainingSessionFactory
import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestTrainingSession:

    def test_selector_training_session_per_client_test(self, session_env):
        tenant = session_env["tenant"]
        coach = session_env["coach"]
        client = session_env["client"]
        client2 = session_env["client2"]

        s1 = TrainingSessionFactory(
            client=client,
            gym=tenant,
            coach=coach,
            is_active=False,
            start=timezone.now()
        )
        s1 = TrainingSessionFactory(
            client=client,
            gym=tenant,
            coach=coach,
            is_active=True,
            start=timezone.now()
        )
        s1 = TrainingSessionFactory(
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
