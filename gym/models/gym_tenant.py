from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from core.models.behaviours import TimeStampable


class GymTenant(TenantMixin, TimeStampable):
    auto_create_schema = True

    name = models.CharField(max_length=255)


class Domain(DomainMixin):
    pass
