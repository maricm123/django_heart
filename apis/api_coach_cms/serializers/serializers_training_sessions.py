from rest_framework import serializers
from apis.api_coach_cms.serializers.serializers_users import ClientInfoSerializer
from training_session.models import TrainingSession
from user.models import Client


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
    client_name = serializers.CharField(source="client.name")

    class Meta:
        model = TrainingSession
        fields = '__all__'


class SendTrainingSessionReportEmailSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    recipient_email = serializers.EmailField()

    def validate_session_id(self, value):
        try:
            session = TrainingSession.objects.get(id=value, end__isnull=False)
            return session
        except TrainingSession.DoesNotExist:
            raise serializers.ValidationError("Training session not found or not finished.")

    def validate(self, data):
        session = data.get('session_id')
        coach = self.context['request'].user.coach
        
        # Proveravamo da li je trenutni korisnik trener ove sesije
        if session.coach != coach:
            raise serializers.ValidationError("You are not the coach of this session.")
        
        data['session'] = session
        return data
