from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from apis.api_coach_cms.serializers.serializers_users import (
    CoachInfoSerializer,
    CustomTokenObtainPairSerializer,
    ClientInfoSerializer,
    CreateClientSerializer,
    UserInfoNameFieldsSerializer, ClientUpdateSerializer,
)
from core.utils import get_logger, AppLog
from user.log_templates import LOG_COACH_LOGGED_IN
from user.models import Client
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

logger = get_logger(__name__)


class CurrentCoachInfoView(generics.RetrieveUpdateAPIView):
    """
    View for getting current logged coach information.
    """
    serializer_class = CoachInfoSerializer
    # We need to create custom permissions
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            # test log
            AppLog(logger, LOG_COACH_LOGGED_IN, coach=self.request.user.coach)
            return self.request.user.coach
        except ObjectDoesNotExist:
            raise Http404

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class LoginCoachView(TokenObtainPairView):
    """
    View to handle login, we inherit View from simple_jwt library.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class GetAllClientsFromCoachNotActiveSessionView(generics.ListAPIView):
    """
    View for getting all the clients of coach, but do not show clients that are
    in active training session.
    """
    class OutputSerializer(serializers.ModelSerializer):
        user = UserInfoNameFieldsSerializer()

        class Meta:
            model = Client
            fields = ["id", "user", "weight", "height", "gender"]

    permission_classes = [IsAuthenticated]
    serializer_class = OutputSerializer

    def get_queryset(self):
        return (
            Client.objects
            .filter(coach=self.request.user.coach)
            .select_related('user')
            .exclude(sessions__is_active=True)
            .distinct()
        )


class GetAllClientsFromCoach(generics.ListAPIView):
    """
    List of clients for "Client list" page
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ClientInfoSerializer

    def get_queryset(self):
        return Client.objects.filter(coach=self.request.user.coach).select_related('user')


class CreateClientView(generics.CreateAPIView):
    """
    Coach adding new client.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CreateClientSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        new_client = Client.objects.get(pk=serializer.validated_data["pk"])
        return Response(ClientInfoSerializer(new_client).data, status=status.HTTP_201_CREATED)


class UpdateClientView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClientUpdateSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Client.objects.filter(coach=self.request.user.coach)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class GetClientDetailsView(generics.RetrieveAPIView):
    class OutputSerializer(serializers.ModelSerializer):
        user = UserInfoNameFieldsSerializer()
        class Meta:
            model = Client
            fields = '__all__'
    permission_classes = [IsAuthenticated]
    serializer_class = OutputSerializer
    lookup_field = "id"

    def get_object(self):
        return get_object_or_404(Client, id=self.kwargs['id'])


class DeleteClientView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    queryset = Client.objects.all()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft delete here
        instance.delete()
        return Response(status=204)
