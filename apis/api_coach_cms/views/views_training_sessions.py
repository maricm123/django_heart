from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from apis.api_coach_cms.serializers.serializers_training_sessions import (
    GetActiveTrainingSessionsSerializer,
    GetAllTrainingSessionsPerClientSerializer, GetAllTrainingSessionsPerCoachSerializer,
    GetTrainingSessionSerializer,
)
from training_session.models import TrainingSession
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from training_session.selectors import training_session_per_client_list_data
from training_session.services import training_session_update


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
        return TrainingSession.objects.filter(coach=self.request.user.coach, is_active=False).order_by('-start')


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

    def patch(self, request, *args, **kwargs):
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
