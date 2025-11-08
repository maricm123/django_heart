from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apis.api_coach_cms.serializers.serializers_training_sessions import (
    GetActiveTrainingSessionsSerializer,
    GetAllTrainingSessionsPerClientSerializer, GetAllTrainingSessionsPerCoachSerializer,
    GetUpdateDeleteTrainingSessionSerializer,
)
from training_session.models import TrainingSession
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from training_session.selectors import training_session_per_client_list


class GetActiveTrainingSessionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetActiveTrainingSessionsSerializer

    def get_queryset(self):
        return TrainingSession.objects.filter(coach=self.request.user.coach, is_active=True)


# class GetAllTrainingSessionsPerClientView(generics.ListAPIView):
#     class OutputSerializer(serializers.Serializer):
#
#     permission_classes = [IsAuthenticated]
#     # serializer_class = GetAllTrainingSessionsPerClientSerializer
#     lookup_field = 'id'
#
#
#     def get_queryset(self):
#         client_id = self.kwargs.get('id')
#         return TrainingSession.objects.filter(client__id=client_id, is_active=False).order_by('-start')
class GetAllTrainingSessionsPerClientView(APIView):
    class OutputSerializer(serializers.Serializer):
        name = serializers.CharField()
        start = serializers.DateTimeField()
        end = serializers.DateTimeField()
        calories_burned = serializers.FloatField()
    permission_classes = [IsAuthenticated]
    # serializer_class = GetAllTrainingSessionsPerClientSerializer
    # lookup_field = 'id'

    def get(self, request, id):
        training_session_per_client = training_session_per_client_list(client_id=id)

        data = self.OutputSerializer(training_session_per_client, many=True).data

        return Response(data)

    # def get_queryset(self):
    #     client_id = self.kwargs.get('id')
    #     return TrainingSession.objects.filter(client__id=client_id, is_active=False).order_by('-start')


class GetAllTrainingSessionsPerCoachView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetAllTrainingSessionsPerCoachSerializer

    def get_queryset(self):
        return TrainingSession.objects.filter(coach=self.request.user.coach, is_active=False).order_by('-start')


class GetUpdateDeleteTrainingSessionView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetUpdateDeleteTrainingSessionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return TrainingSession.objects.filter(
            id=self.kwargs['id'], is_active=False).select_related('coach', 'client')
