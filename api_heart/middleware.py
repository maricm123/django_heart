from django_tenants.utils import get_tenant_model, get_public_schema_name
from django.db import connection


# class TenantWebSocketMiddleware:
#     def __init__(self, inner):
#         self.inner = inner
#
#     def __call__(self, scope):
#         host = scope['headers']
#         host_header = next((v for k, v in host if k == b'host'), b'').decode()
#         domain = host_header.split(':')[0]
#         print(domain, "DOMAIN")
#         TenantModel = get_tenant_model()
#         try:
#             tenant = TenantModel.objects.get(domain_url=domain)
#         except TenantModel.DoesNotExist:
#             connection.set_schema_to_public()
#         else:
#             connection.set_tenant(tenant)
#         return self.inner(scope)
