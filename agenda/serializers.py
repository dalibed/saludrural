from rest_framework import serializers


class AgendaCreateRangeSerializer(serializers.Serializer):
    id_usuario_medico = serializers.IntegerField()
    fecha = serializers.DateField()
    hora_inicio = serializers.TimeField()
    hora_fin = serializers.TimeField()


class AgendaToggleSerializer(serializers.Serializer):
    id_usuario_medico = serializers.IntegerField()
    disponible = serializers.BooleanField()


class AgendaSerializer(serializers.Serializer):
    id_agenda = serializers.IntegerField()
    fecha = serializers.DateField()
    hora = serializers.TimeField()
    disponible = serializers.BooleanField()

