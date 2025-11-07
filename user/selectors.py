# Selectors are for fetching data
from user.caches import get_cached_client, set_cached_client
from user.models import Client
from django.utils import timezone


def get_client_with_cache(client_id: int) -> Client:
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


#  Too complicated to be property of model
def sessions_this_month(training_sessions):
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    return training_sessions.filter(
        start__gte=start_of_month,
        start__lte=now
    )
