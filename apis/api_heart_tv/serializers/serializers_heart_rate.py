from rest_framework import serializers
from heart.models.heart_rate_record import HeartRateRecord
from training_session.models import TrainingSession


class HeartRateRecordSerializer(serializers.ModelSerializer):
    training_session = serializers.PrimaryKeyRelatedField(
        queryset=TrainingSession.objects.select_related('gym', 'coach__user', 'client')
    )
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = HeartRateRecord
        fields = ['id', 'client', 'client_name', 'device_id', 'bpm', 'timestamp', 'training_session']
