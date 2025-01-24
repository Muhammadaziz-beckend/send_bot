from rest_framework import serializers


class AuthLoginSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()
