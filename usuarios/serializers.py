from rest_framework import serializers

ROL_CHOICES = ['Paciente', 'Medico', 'Administrador']

class UsuarioCreateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    documento = serializers.CharField(max_length=50)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    correo = serializers.EmailField(max_length=100)
    telefono = serializers.CharField(max_length=20, required=False, allow_null=True)
    contrasena = serializers.CharField(max_length=100)
    rol = serializers.ChoiceField(choices=ROL_CHOICES)

class UsuarioUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    correo = serializers.EmailField(max_length=100)
    telefono = serializers.CharField(max_length=20, required=False, allow_null=True)

class UsuarioSerializer(serializers.Serializer):
    id_usuario = serializers.IntegerField()
    nombre = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    documento = serializers.CharField(max_length=50)
    correo = serializers.CharField(max_length=100)
    telefono = serializers.CharField(allow_null=True)
    rol = serializers.CharField(max_length=20)
    activo = serializers.BooleanField()
    motivo_inactivacion = serializers.CharField(allow_null=True)
    fecha_inactivacion = serializers.DateTimeField(allow_null=True)
