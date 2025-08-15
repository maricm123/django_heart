from rest_framework import serializers
from heart.models.heart_rate_record import HeartRateRecord


class HeartRateRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeartRateRecord
        fields = ['id', 'client', 'device_id', 'bpm', 'timestamp', 'training_session']
