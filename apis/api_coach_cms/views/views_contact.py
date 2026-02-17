from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, throttling

from core.emails import send_contact_email, ContactEmailPayload


class ContactFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    company = serializers.CharField(max_length=160, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=60, required=False, allow_blank=True)
    message = serializers.CharField(max_length=4000)

    kind = serializers.ChoiceField(
        choices=[("contact", "contact"), ("demo", "demo")],
        required=False,
        default="contact",
    )

    website = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs.get("website"):
            raise serializers.ValidationError("Invalid submission.")
        return attrs


class ContactFormThrottle(throttling.AnonRateThrottle):
    rate = "10/hour"


class SendMailContactFormView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ContactFormThrottle]

    def post(self, request):
        ser = ContactFormSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        payload = ContactEmailPayload(
            name=data["name"],
            email=data["email"],
            message=data["message"],
            kind=data.get("kind", "contact"),
            company=data.get("company", ""),
            phone=data.get("phone", ""),
        )

        send_contact_email(payload)

        return Response({"ok": True}, status=status.HTTP_200_OK)
