from django.shortcuts import get_object_or_404
from rest_framework import serializers

from gym.models import GymTenant
from training_session.models import TrainingSession
from user.models import Coach
from user.models.client import Client


class CreateTrainingSessionSerializer(serializers.Serializer):
    title = serializers.CharField()
    start = serializers.DateTimeField(required=True)
    client_id = serializers.IntegerField(required=True)

    def validate_start(self, value):
        print(value, "Value start")
        # start_class = datetime.fromisoformat(value)
        # print(start_class, "START CLASS")
        return value

    def validate_client_id(self, value):
        return get_object_or_404(Client, id=value)

    def validate(self, data):
        start = data.get('start')
        title = data.get('title')
        client_id = data.get('client_id')
        coach_id = data.get('coach_id')

        user = self.context['request'].user
        coach = Coach.objects.get(user=user)

        session = TrainingSession.start_session(
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

    class Meta:
        model = TrainingSession
        fields = '__all__'


class FinishTrainingSessionSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        if instance.end is None:
            instance.end_session()
            return instance
