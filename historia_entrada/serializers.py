from rest_framework import serializers


class HistoriaEntradaCreateSerializer(serializers.Serializer):
    id_usuario_medico = serializers.IntegerField()
    id_cita = serializers.IntegerField()
    diagnostico = serializers.CharField()
    tratamiento = serializers.CharField()
    notas = serializers.CharField(allow_blank=True, required=False)


class HistoriaEntradaUpdateSerializer(serializers.Serializer):
    id_usuario_medico = serializers.IntegerField()
    diagnostico = serializers.CharField()
    tratamiento = serializers.CharField()
    notas = serializers.CharField(allow_blank=True, required=False)
