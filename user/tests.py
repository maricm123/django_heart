import pytest
from django.contrib.auth import get_user_model
User = get_user_model()


@pytest.mark.django_db
class TestUser:
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

    # def test_create_client_user_normalizes_email(self):
    #     user = User.objects.create_client_user(
    #         email="TEST@example.com",
    #         first_name="Nikola",
    #         last_name="Jovanovic",
    #     )
    #     assert user.email == "test@example.com"  # normalized

    def test_debug_tenant_env(db, tenant):
        from django.db import connection
        from django_tenants.utils import tenant_context
        print("PUBLIC tables:", connection.introspection.table_names())
        with tenant_context(tenant):
            print("TENANT:", tenant.schema_name)
            print("TENANT tables:", connection.introspection.table_names())
