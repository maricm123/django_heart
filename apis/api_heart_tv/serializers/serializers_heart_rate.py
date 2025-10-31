from rest_framework import serializers
from heart.models.heart_rate_record import HeartRateRecord
from training_session.models import TrainingSession
from training_session.services import get_training_session_from_cache
from user.models import Client


class HeartRateRecordSerializer(serializers.ModelSerializer):
    # training_session = serializers.PrimaryKeyRelatedField(
    #     queryset=TrainingSession.objects.select_related('gym', 'coach__user', 'client'),
    #     required=True
    # )
    # client_name = serializers.CharField(source="client.user.name", read_only=True)
    # coach_name = serializers.CharField(source="training_session.coach.user.name", read_only=True)
    seconds = serializers.IntegerField(required=True, write_only=True)
    # client = serializers.PrimaryKeyRelatedField(
    #     queryset=Client.objects.select_related('user'),
    #     required=True
    # )
    training_session_id = serializers.IntegerField(required=True)

    class Meta:
        model = HeartRateRecord
        fields = ['id', 'device_id', 'bpm', 'timestamp', 'training_session_id', 'seconds']

    def create(self, validated_data):
        # Remove non-model fields before creating the instance
        seconds = validated_data.pop('seconds', None)

        training_session_id = validated_data['training_session_id']
        validated_data['training_session'] = get_training_session_from_cache(training_session_id)
        validated_data['client'] = validated_data['training_session'].client
        instance = HeartRateRecord.objects.create(**validated_data)

        # Optionally: store or use `seconds` somewhere
        if seconds is not None:
            instance._seconds = seconds  # temporarily attach to instance for use in view

        return instance
