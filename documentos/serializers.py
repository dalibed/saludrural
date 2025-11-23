from rest_framework import serializers


class DocumentoUploadSerializer(serializers.Serializer):
    id_usuario_medico = serializers.IntegerField(required=True)
    id_tipo_documento = serializers.IntegerField(required=True)
    archivo = serializers.CharField(max_length=200, required=True, allow_blank=False)


class DocumentoSerializer(serializers.Serializer):
    id_documento = serializers.IntegerField()
    archivo = serializers.CharField()
    fecha_subida = serializers.DateField()
    estado = serializers.CharField()
    id_tipo_documento = serializers.IntegerField()
    tipo_documento = serializers.CharField()
    descripcion = serializers.CharField()


class DocumentoValidacionSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=['Pendiente', 'Aprobado', 'Rechazado'])
    observaciones = serializers.CharField(allow_blank=True, allow_null=True)
    id_usuario_admin = serializers.IntegerField()
