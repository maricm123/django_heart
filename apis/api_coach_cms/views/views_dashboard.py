from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.selectors import get_dashboard_info


class DashboardInformationsView(generics.GenericAPIView):
    class OutputSerializer(serializers.Serializer):
        gym_name = serializers.CharField(required=True)
        coach_name = serializers.CharField(required=True)

    permission_classes = [IsAuthenticated]

    def get(self, request):
        gym_tenant = self.request.tenant.name
        print(gym_tenant)
        dashboard_info = get_dashboard_info(self.request)

        data = self.OutputSerializer(dashboard_info).data

        return Response(data)
