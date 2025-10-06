from django.shortcuts import get_object_or_404
from rest_framework import serializers
from apis.api_coach_cms.serializers.serializers_users import ClientInfoSerializer
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
    client = ClientInfoSerializer()

    class Meta:
        model = TrainingSession
        fields = '__all__'


class FinishTrainingSessionSerializer(serializers.Serializer):
    calories_at_end = serializers.DecimalField(write_only=True, max_digits=8, decimal_places=2)
    seconds = serializers.IntegerField(write_only=True)

    def update(self, instance, validated_data):
        calories_at_end = validated_data.get('calories_at_end')
        seconds = validated_data.get('seconds')
        if instance.end is None:
            instance.end_session(calories_at_end, seconds)
            return instance
