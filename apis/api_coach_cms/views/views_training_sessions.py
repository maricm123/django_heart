from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apis.api_coach_cms.serializers.serializers_training_sessions import GetActiveTrainingSessionsSerializer
from training_session.models import TrainingSession


class GetActiveTrainingSessionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetActiveTrainingSessionsSerializer

    def get_queryset(self):
        return TrainingSession.objects.filter(coach=self.request.user.coach, is_active=True)
