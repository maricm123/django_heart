from django.core.cache import cache
from client.models import Client

CACHE_TIMEOUT = 60 * 60  # 1 hour


def get_client_cache_key(client_id: int) -> str:
    return f"client:{client_id}"


def get_cached_client(client_id: int) -> Client | None:
    """Return client from cache, or None if not cached."""
    key = get_client_cache_key(client_id)
    return cache.get(key)


def set_cached_client(client_id: int, client: Client):
    """Set client in cache."""
    key = get_client_cache_key(client_id)
    cache.set(key, client, timeout=CACHE_TIMEOUT)


def delete_cached_client(client_id: int):
    """Remove client from cache."""
    key = get_client_cache_key(client_id)
    cache.delete(key)

