from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.serializers import EmailFieldSerializer
from user.models import Client, GymManager
from phonenumber_field.serializerfields import PhoneNumberField
from user.services import client_create

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'


class UserInfoNameFieldsSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'birth_date')


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

        tenant_id = getattr(self.user.coach.gym, 'id', None)
        print(tenant_id)
        if tenant_id:
            refresh['tenant_id'] = tenant_id
            access['tenant_id'] = tenant_id

        # we ll se do we need role in response, maybe we have that through access token
        # data['role'] = self.user.role
        data['refresh'] = str(refresh)
        data['access'] = str(access)
        data['tenant_id'] = tenant_id

        return data


class CreateClientSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    birth_date = serializers.DateField(write_only=True)
    # profile_picture_url = serializers.URLField()
    # Client fields
    gender = serializers.CharField(max_length=100, required=True)
    weight = serializers.FloatField(required=True)
    height = serializers.FloatField(required=True)
    phone_number = PhoneNumberField(required=False, allow_null=True)
    max_heart_rate = serializers.IntegerField(required=False, allow_null=True)
    auto_calculate_max_hr = serializers.BooleanField(required=True)

    def validate_gender(self, value):
        allowed_genders = ["Male", "Female"]
        if value not in allowed_genders:
            raise serializers.ValidationError(
                f"Gender must be one of {', '.join(allowed_genders)}."
            )
        return value

    def validate_max_heart_rate(self, value):
        if value is None:
            return value
        if value < 0:
            raise serializers.ValidationError("Value cannot be negative.")
        if value < 50:
            raise serializers.ValidationError("Max heart rate must be at least 50.")
        return value

    def validate(self, data):
        coach = self.context["request"].user.coach

        # split data into user + client
        user_data = {
            "email": data.pop("email"),
            "first_name": data.pop("first_name"),
            "last_name": data.pop("last_name"),
            "birth_date": data.pop("birth_date"),
            "phone_number": data.pop("phone_number"),
            # "profile_picture_url": data.pop("profile_picture_url"),
        }
        client_data = data

        client = client_create(user_data=user_data, client_data=client_data, coach=coach)

        data["pk"] = client.pk

        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'birth_date',)


class ClientUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()
    max_heart_rate = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Client
        fields = ('id', 'user', 'weight', 'height', 'gender', 'max_heart_rate', 'auto_calculate_max_hr')

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


class CoachUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()

    class Meta:
        model = Client
        fields = ('id', 'user', )

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


class ForgotPasswordSerializer(EmailFieldSerializer):
    def validate(self, attrs):
        pass


class ResetPasswordConfirmSerializer(serializers.Serializer):
    pass