from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apis.api_coach_cms.mixins import TrainingSessionMixin
from apis.api_coach_cms.serializers.serializers_training_sessions import (
    GetActiveTrainingSessionsSerializer,
    GetAllTrainingSessionsPerCoachSerializer,
    GetTrainingSessionSerializer,
)
from training_session.models import TrainingSession
from rest_framework import serializers
from training_session.selectors import training_session_per_client_list_data
from training_session.services import training_session_update
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class GetActiveTrainingSessionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetActiveTrainingSessionsSerializer

    def get_queryset(self):
        return TrainingSession.objects.filter(coach=self.request.user.coach, is_active=True)


class GetAllTrainingSessionsPerClientView(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        title = serializers.CharField()
        start = serializers.DateTimeField()
        end = serializers.DateTimeField()
        calories_burned = serializers.DecimalField(max_digits=5, decimal_places=1)
        client = serializers.CharField()
        coach = serializers.CharField()
        duration = serializers.IntegerField()
        summary_metrics = serializers.JSONField()

    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        training_session_per_client = training_session_per_client_list_data(client_id=id)

        data = self.OutputSerializer(training_session_per_client, many=True).data

        return Response(data)


class GetAllTrainingSessionsPerCoachView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetAllTrainingSessionsPerCoachSerializer

    def get_queryset(self):
        return TrainingSession.objects.filter(
            coach=self.request.user.coach, is_active=False).order_by('-start')


class GetTrainingSessionView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetTrainingSessionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return TrainingSession.objects.filter(
            id=self.kwargs['id'], is_active=False).select_related('coach', 'client')


class DeleteTrainingSessionView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    queryset = TrainingSession.objects.all()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft delete here
        instance.delete()
        return Response(status=204)


class UpdateTrainingSessionView(generics.GenericAPIView):
    """
    NOT finished, we need to brainstorm this
    """
    class TrainingSessionOutputSerializer(serializers.Serializer):
        title = serializers.CharField()

    class UpdateTrainingSessionInputSerializer(serializers.ModelSerializer):
        class Meta:
            model = TrainingSession
            fields = ['title', ]

    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    queryset = TrainingSession.objects.all()

    input_serializer_class = UpdateTrainingSessionInputSerializer
    output_serializer_class = TrainingSessionOutputSerializer

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return self.output_serializer_class
        return self.input_serializer_class

    def patch(self, request):
        training_session = self.get_object()

        serializer = self.input_serializer_class(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        updated = training_session_update(
            training_session=training_session,
            data=serializer.validated_data
        )

        return Response(
            self.output_serializer_class(updated).data
        )


class ForceDeleteActiveTrainingSessionView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    queryset = TrainingSession.objects.all()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft delete here
        instance.force_delete_active_training_session()
        return Response(status=204)


class PauseActiveTrainingSessionView(
    APIView,
    TrainingSessionMixin
):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        actor = request.user
        coach = getattr(actor, "coach", None)
        if not coach:
            return Response({"detail": "Only coaches can pause sessions."}, status=status.HTTP_403_FORBIDDEN)

        training_session = TrainingSessionMixin.get_training_session_with_id(self, id=id)

        if not training_session.is_active:
            return Response({"detail": "Session is not active."}, status=status.HTTP_400_BAD_REQUEST)

        if training_session.coach_id != coach.id:
            return Response({"detail": "You can pause only your sessions."}, status=status.HTTP_403_FORBIDDEN)

        training_session.pause()
        training_session.save(update_fields=["paused_at"])

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"gym_{coach.gym_id}",
            {
                "type": "gym_data",
                "event": "session_pause",
                "client_id": training_session.client_id,
                "paused": training_session.is_paused,
                "paused_at": training_session.paused_at.isoformat() if training_session.paused_at else None,
                "paused_seconds": training_session.total_paused_seconds or 0,
            },
        )

        return Response({
            "id": training_session.id,
            "client_id": training_session.client_id,
            "paused": training_session.is_paused,
            "paused_at": training_session.paused_at,
            "paused_seconds": training_session.total_paused_seconds or 0,
        }, status=status.HTTP_200_OK)


class ResumeActiveTrainingSessionView(
    APIView,
    TrainingSessionMixin
):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        actor = request.user
        coach = getattr(actor, "coach", None)
        if not coach:
            return Response({"detail": "Only coaches can resume sessions."}, status=status.HTTP_403_FORBIDDEN)

        training_session = TrainingSessionMixin.get_training_session_with_id(self,id=id)

        if not training_session.is_active:
            return Response({"detail": "Session is not active."}, status=status.HTTP_400_BAD_REQUEST)

        if training_session.coach_id != coach.id:
            return Response({"detail": "You can resume only your sessions."}, status=status.HTTP_403_FORBIDDEN)

        was_paused = training_session.is_paused
        training_session.resume()

        training_session.save(update_fields=["paused_at", "total_paused_seconds"] if was_paused else ["paused_at"])

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"gym_{coach.gym_id}",
            {
                "type": "gym_data",
                "event": "session_pause",
                "client_id": training_session.client_id,
                "paused": training_session.is_paused,
                "paused_at": training_session.paused_at.isoformat() if training_session.paused_at else None,
                "paused_seconds": training_session.total_paused_seconds or 0,
            },
        )

        return Response({
            "id": training_session.id,
            "client_id": training_session.client_id,
            "paused": training_session.is_paused,
            "paused_at": training_session.paused_at,
            "paused_seconds": training_session.total_paused_seconds or 0,
        }, status=status.HTTP_200_OK)
