from rest_framework import serializers

class MedicoSerializer(serializers.Serializer):
    id_medico = serializers.IntegerField()
    id_usuario = serializers.IntegerField()
    nombre = serializers.CharField()
    apellidos = serializers.CharField()
    documento = serializers.CharField()
    correo = serializers.CharField()
    telefono = serializers.CharField()
    licencia = serializers.CharField(allow_null=True)
    anios_experiencia = serializers.IntegerField(allow_null=True)
    descripcion_perfil = serializers.CharField(allow_null=True)
    foto = serializers.CharField(allow_null=True)
    email = serializers.CharField(allow_null=True)
    vereda = serializers.CharField(allow_null=True)
    estado_validacion = serializers.CharField()
    activo = serializers.BooleanField()


class MedicoUpdateSerializer(serializers.Serializer):
    licencia = serializers.CharField(max_length=50, allow_null=True)
    anios_experiencia = serializers.IntegerField(allow_null=True)
    descripcion_perfil = serializers.CharField(allow_null=True)
    foto = serializers.CharField(max_length=200, allow_null=True)
    email = serializers.CharField(max_length=100, allow_null=True)
    vereda = serializers.CharField(max_length=100, allow_null=True)


class MedicoEstadoSerializer(serializers.Serializer):
    id_medico = serializers.IntegerField()
    id_usuario = serializers.IntegerField()
    nombre = serializers.CharField()
    apellidos = serializers.CharField()
    usuario_activo = serializers.BooleanField()
    estado_validacion = serializers.CharField()
    total_tipos_documento = serializers.IntegerField()
    total_tipos_subidos = serializers.IntegerField()
    total_aprobados = serializers.IntegerField()
    total_pendientes = serializers.IntegerField()
    total_rechazados = serializers.IntegerField()
