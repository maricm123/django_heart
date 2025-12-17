from rest_framework import generics, status
from rest_framework import serializers
from rest_framework.response import Response


class DashboardInformationsView(generics.GenericAPIView):
    class OutputSerializer(serializers.Serializer):
        gym_name = serializers.CharField(source="gym_tenant.name")

    def get(self, request):
        dashboard_info = get_dashboard_info()

        data = self.OutputSerializer().data

        return Response(data)
