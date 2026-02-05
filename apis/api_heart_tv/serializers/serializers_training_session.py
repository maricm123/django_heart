from django.shortcuts import get_object_or_404
from rest_framework import serializers
from apis.api_coach_cms.serializers.serializers_users import ClientInfoSerializer
from training_session.models import TrainingSession
from training_session.services import end_training_session
from user.models.client import Client


class CreateTrainingSessionSerializer(serializers.Serializer):
    title = serializers.CharField()
    start = serializers.DateTimeField(required=True)
    client_id = serializers.IntegerField(required=True)

    def validate_client_id(self, value):
        return get_object_or_404(Client, id=value)

    def validate(self, data):
        start = data.get('start')
        title = data.get('title')
        client_id = data.get('client_id')

        coach = self.context['request'].user.coach

        session = TrainingSession.start_training_session(
            start=start,
            title=title,
            client=client_id,
            coach=coach,
            gym=coach.gym,
            is_active=True
        )
        data['id'] = session.id
        return data


class TrainingSessionInfoSerializer(serializers.ModelSerializer):
    start = serializers.DateTimeField()
    client = ClientInfoSerializer()

    class Meta:
        model = TrainingSession
        fields = '__all__'


class FinishTrainingSessionSerializer(serializers.Serializer):
    calories_at_end = serializers.DecimalField(write_only=True, max_digits=8, decimal_places=2)
    seconds = serializers.IntegerField(write_only=True)

    def update(self, training_session_instance, validated_data):
        calories_at_end = validated_data.get('calories_at_end')
        seconds = validated_data.get('seconds')
        if training_session_instance.end is None:
            end_training_session(training_session_instance, calories_at_end, seconds)
            return training_session_instance
