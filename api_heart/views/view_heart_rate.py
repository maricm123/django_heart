from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from heart.models.heart_rate_record import HeartRateRecord
from ..serializers.serializers_heart_rate import HeartRateRecordSerializer


class HeartRateView(generics.CreateAPIView):
    queryset = HeartRateRecord.objects.all()
    serializer_class = HeartRateRecordSerializer


class LatestHeartRateView(APIView):
    def get(self, request):
        latest_record = HeartRateRecord.objects.order_by('-timestamp').first()
        if not latest_record:
            return Response({"detail": "No data"}, status=404)
        serializer = HeartRateRecordSerializer(latest_record)
        return Response(serializer.data)


class HeartRateRecordCreateView(generics.CreateAPIView):
    queryset = HeartRateRecord.objects.all()
    serializer_class = HeartRateRecordSerializer

    def perform_create(self, serializer):
        instance = serializer.save()

        # Emituj poruku websocket-om
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(

            "bpm_group",
            {
                "type": "send_bpm",
                "device_id": instance.device_id,
                "bpm": instance.bpm,
                "timestamp": instance.timestamp.isoformat()
            }
        )


class HeartRateCreateRecordFromFrontendView(generics.CreateAPIView):
    queryset = HeartRateRecord.objects.all()
    serializer_class = HeartRateRecordSerializer

    # def perform_create(self, serializer):
    #     instance = serializer.save()
    #
    #     return instance
