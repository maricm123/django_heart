from client.models import Client
from client.caches.client_cache import (
    get_cached_client,
    set_cached_client,
)


def get_client(client_id: int) -> Client:
    """
    Returns a Client instance.
    First checks the cache, otherwise fetches from DB and caches it.
    """
    client = get_cached_client(client_id)
    if client:
        return client

    # Lazy import pattern not needed unless circular import exists
    client = Client.objects.select_related("user", "gym").get(pk=client_id)
    set_cached_client(client_id, client)
    return client
