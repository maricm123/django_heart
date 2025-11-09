from training_session.caches import get_cached_training_session, set_cached_training_session
from training_session.models import TrainingSession


def get_training_session_from_cache(training_session_id: int):
    """Get training session, cached or fallback from DB"""

    training_session = get_cached_training_session(training_session_id)
    if training_session:
        return training_session

    training_session = (
        TrainingSession.objects
        .select_related('gym', 'coach__user', 'client', 'client__user')
        .get(pk=training_session_id)
    )

    set_cached_training_session(training_session_id, training_session)
    return training_session


def training_session_per_client_list_data(client_id):
    return (TrainingSession.objects.filter(client=client_id, is_active=False)
            .select_related('coach__user', 'client__user')
            .order_by('-start'))
