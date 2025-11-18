from rest_framework import serializers

class PacienteSerializer(serializers.Serializer):
    id_paciente = serializers.IntegerField()
    id_usuario = serializers.IntegerField()
    nombre = serializers.CharField()
    apellidos = serializers.CharField()
    documento = serializers.CharField()
    correo = serializers.CharField()
    telefono = serializers.CharField()
    grupo_sanguineo = serializers.CharField(allow_null=True)
    seguro_medico = serializers.CharField(allow_null=True)
    contacto_emergencia = serializers.CharField(allow_null=True)
    telefono_emergencia = serializers.CharField(allow_null=True)
    activo = serializers.BooleanField()


class PacienteUpdateSerializer(serializers.Serializer):
    grupo_sanguineo = serializers.CharField(max_length=5, allow_null=True)
    seguro_medico = serializers.CharField(max_length=100, allow_null=True)
    contacto_emergencia = serializers.CharField(max_length=100, allow_null=True)
    telefono_emergencia = serializers.CharField(max_length=20, allow_null=True)
