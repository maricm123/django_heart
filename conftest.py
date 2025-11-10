import pytest
from django_tenants.utils import (
    get_tenant_model,
    get_tenant_domain_model,
    tenant_context,
)


@pytest.fixture(scope="function")
def tenant(db):
    """
    Fresh tenant for each test. Ensures the tenant schema is CREATED and MIGRATED.
    """
    Tenant = get_tenant_model()
    Domain = get_tenant_domain_model()

    tenant = Tenant.objects.create(
        schema_name="test_tenant",
        name="Test Tenant",
    )

    # If your Tenant model doesn't have auto_create_schema=True,
    # you MUST explicitly create & sync the schema:
    # if getattr(tenant, "auto_create_schema", False) is not True:
    # sync_schema=True runs migrations for TENANT_APPS in this schema
    tenant.create_schema(check_if_exists=True, sync_schema=True)

    Domain.objects.create(
        domain="test.localhost",
        tenant=tenant,
        is_primary=True,
    )
    return tenant


@pytest.fixture(scope="function", autouse=True)
def _activate_tenant_schema(tenant):
    """
    Auto-activate the tenant schema for every test, so ORM hits tenant tables.
    """
    with tenant_context(tenant):
        yield
