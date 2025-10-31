from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from heart.models.heart_rate_record import HeartRateRecord
from training_session.models import TrainingSession
from training_session.services import get_training_session_from_cache
from ..serializers.serializers_heart_rate import HeartRateRecordSerializer
from django.contrib.auth import get_user_model
from django.core.cache import cache
from ...utils_for_calculating_calories import calculate_current_burned_calories
from user.models import Client
from training_session.caches import get_cached_training_session

User = get_user_model()


class HeartRateView(generics.CreateAPIView):
    queryset = HeartRateRecord.objects.all()
    serializer_class = HeartRateRecordSerializer


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

        print(instance, "INSTANCE")

        seconds = getattr(instance, '_seconds', None)
        print(seconds)

        # training_session = TrainingSession.objects.get(pk=instance.training_session_id)
        training_session = get_training_session_from_cache(training_session_id=instance.training_session_id)
        # client = instance.client
        # client = get_client_from_cache(instance.client.id)
        client = training_session.client
        print(client, "CLIENT FROM TR SESSION")

        list_of_bpms = [record.bpm for record in training_session.heart_rate_records.all()]
        print(list_of_bpms)

        current_calories = (
            calculate_current_burned_calories(
                list_of_bpms,
                client,
                seconds,
            )
        )
        print(current_calories, "CURRENT CAL")

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"bpm_group_tenant_{self.request.user.coach.gym.id}",
            {
                "type": "send_bpm",  # name of method in Consumer class
                "current_calories": current_calories,
                "client_id": client.id,
                "bpm": instance.bpm
            }
        )

        # Also send to the gym-wide group
        async_to_sync(channel_layer.group_send)(
            f"gym_{self.request.user.coach.gym.id}",
            {
                "type": "gym_data",
                "coach_id": self.request.user.coach.id,
                "client_id": client.id,
                "client_name": client.user.name,
                "bpm": instance.bpm,
                "current_calories": current_calories,
                "seconds": seconds
            }
        )
