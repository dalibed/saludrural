from rest_framework import serializers

class EspecialidadCreateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(allow_blank=True)

class AsignarEspecialidadSerializer(serializers.Serializer):
    id_usuario_medico = serializers.IntegerField()
    id_especialidad = serializers.IntegerField()
