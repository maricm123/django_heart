import pytest
from django.contrib.auth import get_user_model
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import get_tenant_model

User = get_user_model()


@pytest.mark.django_db
class TestUser(TenantTestCase):
    def setUp(self):
        super().setUp()
        tenant_model = get_tenant_model()
        self.tenant = tenant_model.objects.create(
            schema_name="test_tenant",
            name="Test Tenant",
            # domain_url="test.localhost",
        )
        self.tenant.save()
        self.tenant.create_schema(check_if_exists=True)
        self.tenant.activate()  # switch schema before tests
    ####################################################################################################
    # Test user query sets
    ####################################################################################################

    def test_create_client_user_success(self):
        user = User.objects.create_client_user(
            first_name="Mika",
            last_name="Maric",
            email="mika@example.com",
        )

        assert user.email == "mika@example.com"
        assert user.first_name == "Mika"
        assert user.last_name == "Maric"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert User.objects.count() == 1

    def test_create_client_user_without_email_raises_error(self):
        with pytest.raises(ValueError, match="You have not provided a valid e-mail address"):
            User.objects.create_client_user(first_name="Ana", last_name="Petrovic")

    def test_create_client_user_normalizes_email(self):
        user = User.objects.create_client_user(
            email="TEST@EXAMPLE.COM",
            first_name="Nikola",
            last_name="Jovanovic",
        )
        assert user.email == "test@example.com"  # normalized
