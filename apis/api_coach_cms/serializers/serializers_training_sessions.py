from rest_framework import serializers
from apis.api_coach_cms.serializers.serializers_users import ClientInfoSerializer
from training_session.models import TrainingSession


class GetActiveTrainingSessionsSerializer(serializers.ModelSerializer):
    client = ClientInfoSerializer(read_only=True)

    class Meta:
        model = TrainingSession
        fields = '__all__'


class GetAllTrainingSessionsPerClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = '__all__'


class GetAllTrainingSessionsPerCoachSerializer(serializers.ModelSerializer):
    client = serializers.CharField(source="client.name")

    class Meta:
        model = TrainingSession
        fields = '__all__'


class GetTrainingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = '__all__'
