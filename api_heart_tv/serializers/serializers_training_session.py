from django.shortcuts import get_object_or_404
from rest_framework import serializers
from training_session.models import TrainingSession
from datetime import datetime

from user.models import User


class CreateTrainingSessionSerializer(serializers.Serializer):
    title = serializers.CharField()
    start = serializers.DateTimeField(required=True)
    user_id = serializers.IntegerField(required=True)

    def validate_start(self, value):
        print(value, "Value start")
        # start_class = datetime.fromisoformat(value)
        # print(start_class, "START CLASS")
        return value

    def validate_user_id(self, value):
        return get_object_or_404(User, id=value)

    def validate(self, data):
        print(data)

        start = data.get('start')
        title = data.get('title')
        user_id = data.get('user_id')

        session = TrainingSession.start_session(
            start=start,
            title=title,
            user=user_id
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
