from rest_framework import serializers


class TokenFieldSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class EmailFieldSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
