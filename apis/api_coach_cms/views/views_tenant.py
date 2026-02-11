from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from gym.models import Domain


class GetCurrentTenant(APIView):
    def get(self, request):
        tenant = getattr(request, "tenant", None)

        from django.db import connection

        print("CURRENT SCHEMA:", connection.schema_name)
        print("TENANT NAME FROM OBJ:", tenant.name if tenant else None)

        schema_name = getattr(tenant, "schema_name", None) or connection.schema_name
        host = request.get_host().split(":")[0]

        domain_obj = Domain.objects.filter(domain=host).first()

        data = {
            "schema_name": schema_name,
            "is_public_schema": schema_name == "public",
            "host": host,
            "tenant": None,
            "domain": None,
        }

        if tenant and schema_name != "public":
            data["tenant"] = {
                "id": getattr(tenant, "id", None),
                "name": getattr(tenant, "name", None),
                "schema_name": getattr(tenant, "schema_name", None),
            }

        if domain_obj:
            data["domain"] = {
                "id": domain_obj.id,
                "domain": domain_obj.domain,
                "is_primary": getattr(domain_obj, "is_primary", None),
                "tenant_id": getattr(domain_obj.tenant, "id", None) if getattr(domain_obj, "tenant", None) else None,
            }

        return Response(data, status=status.HTTP_200_OK)
