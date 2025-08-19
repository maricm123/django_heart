from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apis.api_coach_cms.mixins import ReqContextMixin
from user.models import Coach, Client, GymManager

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CoachInfoSerializer(ReqContextMixin, serializers.ModelSerializer):
    user = UserInfoSerializer()

    class Meta:
        model = Coach
        fields = ('user', 'specialty',)


class ClientInfoSerializer(UserInfoSerializer):
    user = UserInfoSerializer()

    class Meta:
        model = Client
        fields = '__all__'


class GymManagerInfoSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer()

    class Meta:
        model = GymManager
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Overrides the default TokenObtainPairSerializer to return the role in the token response.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        if not self.user.is_coach:
            raise AuthenticationFailed("Not coach.")

        access = refresh.access_token
        # we ll se do we need role in response, maybe we have that through access token
        # data['role'] = self.user.role
        data['refresh'] = str(refresh)
        data['access'] = str(access)
        return data
