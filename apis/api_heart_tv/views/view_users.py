from rest_framework import generics
from apis.api_heart_tv.serializers.serializers_users import UserListSerializer
from user.models.user import User


class GetAllUsers(generics.ListAPIView):
    # queryset = User.objects.all()
    serializer_class = UserListSerializer

    def get_queryset(self):
        return User.objects.all()
