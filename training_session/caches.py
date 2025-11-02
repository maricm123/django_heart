from django.core.cache import cache


def get_training_session_cache_key(training_session_id: int) -> str:
    return f"training_session:{training_session_id}"


def get_cached_training_session(training_session_id: int):
    print("GET TR SESSIONA")
    key = get_training_session_cache_key(training_session_id)
    return cache.get(key)


def set_cached_training_session(training_session_id: int, training_session):
    print("SETOVANJE TR SESSIONA")
    key = get_training_session_cache_key(training_session_id)
    cache.set(key, training_session, timeout=60 * 60)


def delete_cached_training_session(training_session_id: int):
    print("bRISANJE TR SESSIONA CACHE")
    key = get_training_session_cache_key(training_session_id)
    cache.delete(key)
