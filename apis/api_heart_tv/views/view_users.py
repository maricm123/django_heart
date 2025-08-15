from rest_framework import generics
from apis.api_heart_tv.serializers.serializers_users import (
    UserListSerializer,
ClientListSerializer,
)
from user.models.user import User
from user.models.client import Client


class GetAllUsersView(generics.ListAPIView):
    # queryset = User.objects.all()
    serializer_class = UserListSerializer

    def get_queryset(self):
        return User.objects.all()


class GetAllClientsView(generics.ListAPIView):
    # queryset = User.objects.all()
    serializer_class = ClientListSerializer

    def get_queryset(self):
        return Client.objects.all()
