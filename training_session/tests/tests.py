import pytest
from django.contrib.auth import get_user_model

from training_session.services import end_training_session

User = get_user_model()


@pytest.mark.django_db
class TestTrainingSession:
    ####################################################################################################
    # Test functions for calories
    ####################################################################################################
    def test_end_training_session_updates_fields(training_session):
        result = end_training_session(training_session, 300.5, 1800)
        assert not result.is_active
