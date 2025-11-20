"""
Serializers para el módulo de Usuarios

Validan y transforman datos para operaciones CRUD de usuarios.
Mantienen el patrón del proyecto: serializers.Serializer (no ModelSerializer)
porque trabajamos con Stored Procedures, no con el ORM de Django.

IMPORTANTE:
- La contraseña se hashea ANTES de enviarla al SP
- El SP recibe la contraseña ya hasheada
- NO hay que modificar los SPs existentes
"""

from rest_framework import serializers
from django.contrib.auth.hashers import make_password


# Opciones válidas de rol
ROL_CHOICES = ['Paciente', 'Medico', 'Administrador']


class UsuarioCreateSerializer(serializers.Serializer):
    """
    Serializer para crear un nuevo usuario.
    
    Valida los datos de entrada y hashea la contraseña antes de
    enviarla al stored procedure.
    
    Uso:
        serializer = UsuarioCreateSerializer(data=request.data)
        if serializer.is_valid():
            # La contraseña ya está hasheada en validated_data
            sp_usuario_create(**serializer.validated_data)
    """
    
    nombre = serializers.CharField(
        max_length=100,
        help_text="Nombre del usuario"
    )
    
    apellidos = serializers.CharField(
        max_length=100,
        help_text="Apellidos del usuario"
    )
    
    documento = serializers.CharField(
        max_length=50,
        help_text="Número de documento de identidad (único)"
    )
    
    fecha_nacimiento = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Fecha de nacimiento del usuario (formato: YYYY-MM-DD)"
    )
    
    correo = serializers.EmailField(
        max_length=100,
        help_text="Correo electrónico (único, usado para login)"
    )
    
    telefono = serializers.CharField(
        max_length=20,
        required=False,
        allow_null=True,
        help_text="Número de teléfono"
    )
    
    contrasena = serializers.CharField(
        max_length=255,  # Aumentado para soportar el hash completo
        write_only=True,  # No se incluye en responses
        style={'input_type': 'password'},  # Para browsable API
        help_text="Contraseña del usuario (será hasheada automáticamente)"
    )
    
    rol = serializers.ChoiceField(
        choices=ROL_CHOICES,
        help_text="Rol del usuario en el sistema"
    )
    
    # Campos adicionales específicos por rol (opcionales)
    # Estos se usan si el SP los requiere
    
    # Para Pacientes
    grupo_sanguineo = serializers.CharField(
        max_length=5,
        required=False,
        allow_null=True,
        help_text="Grupo sanguíneo del paciente (ej: O+, AB-)"
    )
    
    seguro_medico = serializers.CharField(
        max_length=100,
        required=False,
        allow_null=True,
        help_text="Nombre del seguro médico del paciente"
    )
    
    contacto_emergencia = serializers.CharField(
        max_length=100,
        required=False,
        allow_null=True,
        help_text="Nombre del contacto de emergencia"
    )
    
    telefono_emergencia = serializers.CharField(
        max_length=20,
        required=False,
        allow_null=True,
        help_text="Teléfono del contacto de emergencia"
    )
    
    # Para Médicos
    licencia = serializers.CharField(
        max_length=50,
        required=False,
        allow_null=True,
        help_text="Número de licencia médica"
    )
    
    anios_experiencia = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Años de experiencia como médico"
    )
    
    descripcion_perfil = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Descripción del perfil profesional del médico"
    )
    
    def validate_correo(self, value):
        """
        Validación adicional del correo.
        
        Normaliza el correo a minúsculas para evitar duplicados
        por diferencias de mayúsculas/minúsculas.
        
        Args:
            value (str): Correo ingresado
            
        Returns:
            str: Correo normalizado
        """
        return value.lower().strip()
    
    def validate_documento(self, value):
        """
        Validación del documento.
        
        Remueve espacios y caracteres especiales comunes.
        
        Args:
            value (str): Documento ingresado
            
        Returns:
            str: Documento limpio
        """
        # Remover espacios, puntos, guiones
        return value.replace(' ', '').replace('.', '').replace('-', '')
    
    def validate_contrasena(self, value):
        """
        Validación y hasheo de contraseña.
        
        CRÍTICO: Este método hashea la contraseña ANTES de enviarla al SP.
        El SP recibirá la contraseña YA hasheada.
        
        Validaciones:
        - Mínimo 8 caracteres
        - Al menos una letra
        - Al menos un número
        
        Args:
            value (str): Contraseña en texto plano
            
        Returns:
            str: Contraseña hasheada (formato: pbkdf2_sha256$...)
            
        Raises:
            ValidationError: Si la contraseña no cumple requisitos
        """
        # 1. Validar longitud mínima
        if len(value) < 8:
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 8 caracteres"
            )
        
        # 2. Validar que contenga al menos una letra
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos una letra"
            )
        
        # 3. Validar que contenga al menos un número
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos un número"
            )
        
        # 4. Hashear la contraseña
        # make_password usa el algoritmo configurado en settings.py
        # Por defecto: PBKDF2 con SHA256
        return make_password(value)


class UsuarioUpdateSerializer(serializers.Serializer):
    """
    Serializer para actualizar datos de un usuario.
    
    Solo permite actualizar campos no sensibles.
    Para cambiar contraseña, usar el endpoint específico de cambio de contraseña.
    """
    
    nombre = serializers.CharField(
        max_length=100,
        help_text="Nombre del usuario"
    )
    
    apellidos = serializers.CharField(
        max_length=100,
        help_text="Apellidos del usuario"
    )
    
    correo = serializers.EmailField(
        max_length=100,
        help_text="Correo electrónico"
    )
    
    telefono = serializers.CharField(
        max_length=20,
        required=False,
        allow_null=True,
        help_text="Número de teléfono"
    )
    
    def validate_correo(self, value):
        """Normalizar correo a minúsculas."""
        return value.lower().strip()


class UsuarioSerializer(serializers.Serializer):
    """
    Serializer de solo lectura para representar un usuario.
    
    Se usa para retornar información de usuarios en responses.
    NO se usa para validar input.
    """
    
    id_usuario = serializers.IntegerField(
        read_only=True,
        help_text="ID único del usuario"
    )
    
    nombre = serializers.CharField(
        max_length=100,
        help_text="Nombre del usuario"
    )
    
    apellidos = serializers.CharField(
        max_length=100,
        help_text="Apellidos del usuario"
    )
    
    documento = serializers.CharField(
        max_length=50,
        help_text="Documento de identidad"
    )
    
    correo = serializers.CharField(
        max_length=100,
        help_text="Correo electrónico"
    )
    
    telefono = serializers.CharField(
        allow_null=True,
        help_text="Número de teléfono"
    )
    
    rol = serializers.CharField(
        max_length=20,
        help_text="Rol del usuario (Paciente, Medico, Administrador)"
    )
    
    activo = serializers.BooleanField(
        help_text="Indica si el usuario está activo"
    )
    
    motivo_inactivacion = serializers.CharField(
        allow_null=True,
        help_text="Razón por la cual el usuario fue desactivado"
    )
    
    fecha_inactivacion = serializers.DateTimeField(
        allow_null=True,
        help_text="Fecha y hora de desactivación"
    )


# =============================================================================
# NOTAS IMPORTANTES PARA EL DESARROLLADOR
# =============================================================================
#
# 1. HASHEO DE CONTRASEÑAS:
#    - La contraseña se hashea en validate_contrasena()
#    - El SP recibe la contraseña YA hasheada
#    - NO hay que modificar los SPs
#    - El campo contrasena en BD debe ser VARCHAR(255) mínimo
#
# 2. MIGRACIÓN DE DATOS EXISTENTES:
#    Si hay usuarios en BD con contraseñas en texto plano:
#    - Ejecutar script de migración (hash_passwords.py)
#    - Esto se hace UNA SOLA VEZ
#
# 3. VALIDACIONES:
#    - Serializers validan formato y requisitos básicos
#    - SPs validan reglas de negocio (duplicados, etc.)
#    - Ambas capas son importantes
#
# 4. SEGURIDAD:
#    - write_only=True en campos de contraseña
#    - Nunca retornar contraseñas (ni hasheadas)
#    - Validar fortaleza de contraseñas
#
# 5. CAMPOS ADICIONALES POR ROL:
#    - Los campos específicos por rol son opcionales
#    - El SP decide si los requiere según el rol
#    - Si no se envían, el SP puede usar valores por defecto
#
# =============================================================================