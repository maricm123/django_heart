from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apis.api_coach_cms.serializers.serializers_training_sessions import (
    GetActiveTrainingSessionsSerializer,
GetAllTrainingSessionsPerClientSerializer,
)
from training_session.models import TrainingSession


class GetActiveTrainingSessionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetActiveTrainingSessionsSerializer

    def get_queryset(self):
        return TrainingSession.objects.filter(coach=self.request.user.coach, is_active=True)


class GetAllTrainingSessionsPerClientView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetAllTrainingSessionsPerClientSerializer
    lookup_field = 'id'

    def get_queryset(self):
        client_id = self.kwargs.get('id')
        return TrainingSession.objects.filter(client__id=client_id, is_active=False).order_by('-start')
