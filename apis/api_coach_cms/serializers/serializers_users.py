from django.contrib.auth import get_user_model
from rest_framework import serializers

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
    class Meta:
        model = Client
        fields = '__all__'


class GymManagerInfoSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer()

    class Meta:
        model = GymManager
        fields = '__all__'
