from rest_framework import serializers
from heart.models.heart_rate_record import HeartRateRecord
from training_session.models import TrainingSession


class HeartRateRecordSerializer(serializers.ModelSerializer):
    training_session = serializers.PrimaryKeyRelatedField(
        queryset=TrainingSession.objects.select_related('gym', 'coach__user', 'client')
    )
    # client_name = serializers.CharField(source="client.user.name", read_only=True)
    # coach_name = serializers.CharField(source="training_session.coach.user.name", read_only=True)
    seconds = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = HeartRateRecord
        fields = ['id', 'client', 'device_id', 'bpm', 'timestamp', 'training_session', 'seconds']

    def create(self, validated_data):
        # Remove non-model fields before creating the instance
        seconds = validated_data.pop('seconds', None)
        instance = HeartRateRecord.objects.create(**validated_data)

        # Optionally: store or use `seconds` somewhere
        if seconds is not None:
            instance._seconds = seconds  # temporarily attach to instance for use in view

        return instance