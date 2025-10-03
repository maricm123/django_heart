from django.core.cache import cache
from django_tenants.middleware import TenantMainMiddleware


#########################
# TENANT MIDDLEWARE
#########################

class CachedTenantMiddleware(TenantMainMiddleware):
    def get_tenant(self, domain_model, hostname):
        return get_tenant_from_domain(domain_model, hostname)


def get_tenant_from_domain(domain_model, domain_name):
    key = f"tenant_for_domain:{domain_name}"
    tenant = cache.get(key)
    if tenant is None:
        # Hit DB only if not cached
        domain = domain_model.objects.select_related('tenant').get(domain=domain_name)
        tenant = domain.tenant
        cache.set(key, tenant, 60 * 60)  # cache for 1h
    return tenant
