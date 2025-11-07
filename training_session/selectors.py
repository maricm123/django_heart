from training_session.caches import get_cached_training_session, set_cached_training_session


def get_training_session_from_cache(training_session_id: int):
    """Get training session, cached or fallback from DB"""
    from training_session.models import TrainingSession
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
