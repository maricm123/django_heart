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

        seconds = getattr(instance, '_seconds', None)

        # cached_training_session = get_training_session_from_cache(instance.training_session_id)

        # print(cached_training_session)
        # here we are fetching db so we need to get rid of that with cache
        training_session = instance.training_session
        client = training_session.client

        # training_session = cached_training_session
        # client = training_session.client

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

    #  THIS REDUCED TO 3 QUERIES, BUT TEST IF EVERYTHING IS OK!!!!
    # def perform_create(self, serializer):
    #     from django.core.cache import cache
    #     instance = serializer.save()
    #     seconds = getattr(instance, '_seconds', None)
    #
    #     # Get cached training session info
    #     cached_ts = get_training_session_from_cache(instance.training_session_id)
    #     if not cached_ts:
    #         # fallback if cache missed
    #         cached_ts = {
    #             "training_session_id": instance.training_session_id,
    #             "client_id": instance.client_id,
    #         }
    #
    #     training_session = cached_ts
    #     # client_id = cached_ts["client_id"]
    #
    #     # Instead of hitting DB for heart_rate_records, track recent BPMs in cache
    #     bpm_list_key = f"bpm_list:{training_session.id}"
    #     cache_data = cache.get(bpm_list_key, [])
    #     cache_data.append(instance.bpm)
    #     if len(cache_data) > 60:  # e.g. keep last 60 seconds
    #         cache_data = cache_data[-60:]
    #     cache.set(bpm_list_key, cache_data, timeout=60 * 60)
    #
    #     # Use the cached list for calorie calculation
    #     list_of_bpms = cache_data
    #     current_calories = calculate_current_burned_calories(
    #         list_of_bpms,
    #         instance.client,  # we can still use instance.client_id if needed
    #         seconds,
    #     )
    #
    #     channel_layer = get_channel_layer()
    #     gym_id = cached_ts.coach.gym_id  # use gym_id field (no lazy load)
    #
    #     async_to_sync(channel_layer.group_send)(
    #         f"bpm_group_tenant_{gym_id}",
    #         {
    #             "type": "send_bpm",
    #             "current_calories": current_calories,
    #             "client_id": training_session.client.id,
    #             "bpm": instance.bpm
    #         }
    #     )
    #
    #     async_to_sync(channel_layer.group_send)(
    #         f"gym_{gym_id}",
    #         {
    #             "type": "gym_data",
    #             "coach_id": cached_ts.coach_id,
    #             "client_id":  training_session.client.id,
    #             "client_name": getattr(instance.client.user, 'name', ''),  # careful if user not prefetched
    #             "bpm": instance.bpm,
    #             "current_calories": current_calories,
    #             "seconds": seconds
    #         }
    #     )