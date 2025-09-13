from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from heart.models.heart_rate_record import HeartRateRecord
from training_session.models import TrainingSession
from user.models import Client
from ..serializers.serializers_heart_rate import HeartRateRecordSerializer
from django.contrib.auth import get_user_model

from ...utils_for_calculating_calories import calculate_current_burned_calories

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

    def perform_create(self, serializer):
        instance = serializer.save()

        training_session = TrainingSession.objects.get(pk=instance.training_session_id)
        client = Client.objects.get(pk=training_session.client_id)

        list_of_bpms = [record.bpm for record in training_session.heart_rate_records.all()]
        print(list_of_bpms)
        # current_calories = (
        #     self.current_calories_burned(client, list_of_bpms, training_session.start, instance.timestamp))
        current_calories = (
            calculate_current_burned_calories(
                list_of_bpms,
                client,
                training_session,
                instance.timestamp
            )
        )
        print(current_calories, "CURRENT CAL")
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "bpm_group",
            {
                "type": "send_bpm",  # name of method in Consumer class
                "current_calories": current_calories,
                "client_id": client.id,
            }
        )

    # def current_calories_burned(self, user, list_of_bpms, session_start, current_timestamp):
    #     if len(list_of_bpms) != 0:
    #         average_bpm = self.calculate_average_heart_rate(list_of_bpms)
    #
    #         weight = user.weight
    #         print(weight)
    #         age = user.get_age_from_birth_date()
    #         print(age)
    #         duration_in_minutes = self.calculate_current_duration_in_minutes(session_start, current_timestamp)
    #         print(duration_in_minutes)
    #
    #         if average_bpm < 60:
    #             calories = 1 * duration_in_minutes  # 1 kcal/min minimum
    #
    #         if user.gender == 'male':
    #             calories = ((-55.0969 + (0.6309 * average_bpm) + (0.1988 * weight) + (0.2017 * age)) / 4.184) * duration_in_minutes
    #             print(calories, "CALORIES")
    #         else:
    #             calories = ((-20.4022 + (0.4472 * average_bpm) - (0.1263 * weight) + (0.074 * age)) / 4.184) * duration_in_minutes
    #
    #         print(max(round(calories, 2), 0))
    #         return max(round(calories, 2), 0)

    # def current_calories_burned(self, client, list_of_bpms, session_start, current_timestamp):
    #     if not list_of_bpms:
    #         return 0
    #
    #     average_bpm = self.calculate_average_heart_rate(list_of_bpms)
    #     weight = client.weight
    #     age = client.user.get_age_from_birth_date()
    #     duration_in_minutes = self.calculate_current_duration_in_minutes(session_start, current_timestamp)
    #     print(duration_in_minutes, "CURRENT DURATION")
    #
    #     # Ako je trajanje manje od sekunde, vrati 0
    #     if duration_in_minutes <= 0:
    #         return 0
    #
    #     if client.gender == 'male':
    #         calories = ((-55.0969 + (0.6309 * average_bpm) + (0.1988 * weight) + (
    #                     0.2017 * age)) / 4.184) * duration_in_minutes
    #     else:
    #         calories = ((-20.4022 + (0.4472 * average_bpm) - (0.1263 * weight) + (
    #                     0.074 * age)) / 4.184) * duration_in_minutes
    #
    #     # Minimalna vrednost po minuti (npr. 0.8 kcal/min)
    #     min_calories = duration_in_minutes * 0.8
    #
    #     # Uvek vraćaj barem minimalno, zaokruženo na 2 decimale
    #     return round(max(calories, min_calories), 2)

    # def calculate_average_heart_rate(self, list_of_bpms):
    #     average = sum(list_of_bpms) / len(list_of_bpms)
    #     return average


    # def calculate_current_duration_in_minutes(self, start, end):
    #     duration = (end - start).total_seconds() / 60
    #     return duration
