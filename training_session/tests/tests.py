import pytest
from django.contrib.auth import get_user_model
from training_session.selectors import training_session_per_client_list_data
from training_session.services import end_training_session
from training_session.tests.factories import TrainingSessionFactory
from user.tests.factories import ClientFactory, UserFactory, CoachFactory
from django.utils import timezone
User = get_user_model()


@pytest.mark.django_db
class TestTrainingSession:
    ####################################################################################################
    # Test functions for calories
    ####################################################################################################
    # def test_end_training_session_updates_fields(training_session):
    #     result = end_training_session(training_session, 300.5, 1800)
    #     assert not result.is_active
    pass

    def test_selector_training_session_per_client_test(self, tenant):
        coach = CoachFactory(gym=tenant)
        client = ClientFactory(coach=coach, gym=tenant)
        client2 = ClientFactory(coach=coach, gym=tenant)
        training_session = TrainingSessionFactory(
            client=client,
            gym=tenant,
            coach=coach,
            start=timezone.now(),
            is_active=False
        )
        training_session2 = TrainingSessionFactory(
            client=client,
            gym=tenant,
            coach=coach,
            start=timezone.now(),
            is_active=True
        )
        training_session3 = TrainingSessionFactory(
            client=client2,
            gym=tenant,
            coach=coach,
            start=timezone.now(),
            is_active=False
        )

        training_session_list = training_session_per_client_list_data(client.id)
        print(training_session_list)
        assert len(training_session_list) == 1
