from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from heart.models.heart_rate_record import HeartRateRecord
from ..serializers.serializers_heart_rate import HeartRateRecordSerializer
from django.contrib.auth import get_user_model
from heart.utils_for_calculating_calories import calculate_current_burned_calories

User = get_user_model()


class LatestHeartRateView(APIView):
    def get(self, request):
        latest_record = HeartRateRecord.objects.order_by('-timestamp').first()
        if not latest_record:
            return Response({"detail": "No dataaa"}, status=404)
        serializer = HeartRateRecordSerializer(latest_record)
        return Response(serializer.data)


class HeartRateCreateRecordFromFrontendView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = HeartRateRecord.objects.all()
    serializer_class = HeartRateRecordSerializer

    def perform_create(self, serializer):
        instance = serializer.save()

        seconds = getattr(instance, '_seconds', None)

        training_session = instance.training_session
        client = instance.client

        # Here we can maybe do something with cache
        list_of_bpms = [record.bpm for record in training_session.heart_rate_records.all()]

        current_calories = float(calculate_current_burned_calories(list_of_bpms, client, seconds))

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            # Using tenant from request because of middleware
            f"coach_preview_{self.request.tenant.id}",
            {
                "type": "send_bpm",  # name of method in Consumer class
                "current_calories": current_calories,
                "client_id": client.id,
                "bpm": instance.bpm
            }
        )

        # Also send to the gym-wide group
        async_to_sync(channel_layer.group_send)(
            # Using tenant from request because of middleware
            f"gym_{self.request.tenant.id}",
            {
                "type": "gym_data",
                "coach_id": instance.training_session.coach.id,
                "client_id": client.id,
                "client_name": client.user.name,
                "bpm": instance.bpm,
                "current_calories": current_calories,
                "seconds": seconds
            }
        )
