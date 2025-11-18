from rest_framework import serializers


class TipoDocCreateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=50)
    descripcion = serializers.CharField(allow_blank=True, required=False)


class TipoDocUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=50)
    descripcion = serializers.CharField(allow_blank=True, required=False)


class TipoDocSerializer(serializers.Serializer):
    id_tipo_documento = serializers.IntegerField()
    nombre = serializers.CharField()
    descripcion = serializers.CharField()
