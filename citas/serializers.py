from rest_framework import serializers


class CrearCitaSerializer(serializers.Serializer):
    id_usuario_paciente = serializers.IntegerField()
    id_usuario_medico = serializers.IntegerField()
    id_agenda = serializers.IntegerField()
    motivo_consulta = serializers.CharField()


class CancelarCitaSerializer(serializers.Serializer):
    id_usuario = serializers.IntegerField()
    motivo_cancelacion = serializers.CharField(allow_blank=True, required=False)


class CitaSerializer(serializers.Serializer):
    id_cita = serializers.IntegerField()
    estado = serializers.CharField()
    motivo_consulta = serializers.CharField()
    fecha = serializers.DateField()
    hora = serializers.TimeField()
    id_usuario_medico = serializers.IntegerField(allow_null=True)
    id_usuario_paciente = serializers.IntegerField(allow_null=True)

