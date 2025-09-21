from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apis.api_coach_cms.mixins import ReqContextMixin
from user.models import Coach, Client, GymManager

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'


class CoachInfoSerializer(ReqContextMixin, serializers.ModelSerializer):
    user = UserInfoSerializer()

    class Meta:
        model = Coach
        fields = ('user', 'specialty',)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Update client fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


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


class CreateClientSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    birth_date = serializers.DateField(write_only=True)
    is_active = serializers.BooleanField(default=True)
    profile_picture_url = serializers.URLField()
    # Client fields
    gender = serializers.CharField(max_length=100, required=True)
    weight = serializers.FloatField(required=True)
    height = serializers.FloatField(required=True)

    def validate(self, data):
        coach = self.context["request"].user.coach

        # split data into user + client
        user_data = {
            "email": data.pop("email"),
            "first_name": data.pop("first_name"),
            "last_name": data.pop("last_name"),
            "password": data.pop("password"),
            "birth_date": data.pop("birth_date"),
            "is_active": data.pop("is_active"),
            "profile_picture_url": data.pop("profile_picture_url"),
        }
        client_data = data

        client = Client.create(user_data=user_data, client_data=client_data, coach=coach)

        data["pk"] = client.pk

        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'birth_date',)


class ClientDetailUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()

    class Meta:
        model = Client
        fields = ('id', 'user', 'weight', 'height', 'gender')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Update client fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
