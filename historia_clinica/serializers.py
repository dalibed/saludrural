from rest_framework import serializers


class AntecedentesUpdateSerializer(serializers.Serializer):
    antecedentes = serializers.CharField()
