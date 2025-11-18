from rest_framework import serializers

class DiccionarioCreateSerializer(serializers.Serializer):
    id_usuario_admin = serializers.IntegerField()
    termino = serializers.CharField(max_length=100)
    definicion = serializers.CharField()
    causas = serializers.CharField()
    tratamientos = serializers.CharField()


class DiccionarioUpdateSerializer(serializers.Serializer):
    id_usuario_admin = serializers.IntegerField()
    termino = serializers.CharField(max_length=100)
    definicion = serializers.CharField()
    causas = serializers.CharField()
    tratamientos = serializers.CharField()
