from rest_framework import serializers


class AdminIDSerializer(serializers.Serializer):
    id_admin = serializers.IntegerField()
