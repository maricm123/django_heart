from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.response import Response
from apis.api_heart_tv.serializers.serializers_training_session import CreateTrainingSessionSerializer, \
    TrainingSessionInfoSerializer, FinishTrainingSessionSerializer
from training_session.models import TrainingSession


class CreateTrainingSessionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateTrainingSessionSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        new_training_session = TrainingSession.objects.get(
            id=serializer.validated_data['id'],
        )

        return Response(TrainingSessionInfoSerializer(new_training_session).data, status=status.HTTP_201_CREATED)


class FinishTrainingSessionView(generics.UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = FinishTrainingSessionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return TrainingSession.objects.all()

    def update(self, request, *args, **kwargs):
        training_session = self.get_object()
        serializer = self.get_serializer(training_session, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        training_session = TrainingSession.objects.get(id=training_session.id)
        return Response(TrainingSessionInfoSerializer(training_session).data, status=HTTP_200_OK)
