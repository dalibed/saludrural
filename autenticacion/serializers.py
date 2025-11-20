"""
Serializers para el módulo de Autenticación

Estos serializers validan los datos de entrada para operaciones de autenticación.
Usamos serializers.Serializer (no ModelSerializer) porque trabajamos con SPs,
manteniendo la coherencia con el resto del proyecto.
"""

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer para validar datos de login.
    
    Campos:
    - correo: Email del usuario (usado como username)
    - contrasena: Contraseña en texto plano (se valida contra hash en BD)
    
    Uso:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            correo = serializer.validated_data['correo']
            contrasena = serializer.validated_data['contrasena']
    """
    
    correo = serializers.EmailField(
        required=True,
        help_text="Correo electrónico del usuario"
    )
    
    contrasena = serializers.CharField(
        required=True,
        write_only=True,  # No se incluye en responses (seguridad)
        style={'input_type': 'password'},  # Para browsable API
        help_text="Contraseña del usuario"
    )
    
    def validate_correo(self, value):
        """
        Validación adicional del correo.
        
        - Convierte a minúsculas para consistencia
        - Valida formato básico (ya lo hace EmailField, pero podemos agregar más)
        
        Args:
            value (str): Email ingresado
            
        Returns:
            str: Email validado y normalizado
        """
        return value.lower().strip()


class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de login exitoso.
    
    Este serializer NO valida entrada, solo estructura la respuesta.
    Se usa para documentación (Swagger/OpenAPI) y consistencia.
    
    Campos:
    - access: Token JWT de acceso (corta duración: 60 min)
    - refresh: Token JWT de refresco (larga duración: 1 día)
    - usuario: Información básica del usuario autenticado
    """
    
    access = serializers.CharField(
        help_text="Token JWT de acceso. Usar en header: Authorization: Bearer {token}"
    )
    
    refresh = serializers.CharField(
        help_text="Token JWT para renovar el access token cuando expire"
    )
    
    usuario = serializers.DictField(
        help_text="Información básica del usuario autenticado"
    )


class LogoutSerializer(serializers.Serializer):
    """
    Serializer para validar datos de logout.
    
    El logout invalida el refresh token para que no pueda usarse más.
    El access token sigue siendo válido hasta que expire (es stateless).
    
    Campos:
    - refresh: Token de refresco a invalidar
    """
    
    refresh = serializers.CharField(
        required=True,
        help_text="Token de refresco a invalidar"
    )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña.
    
    Validaciones:
    - Contraseña actual correcta
    - Nueva contraseña cumple requisitos mínimos
    - Nueva contraseña y confirmación coinciden
    
    Campos:
    - contrasena_actual: Contraseña actual del usuario
    - contrasena_nueva: Nueva contraseña deseada
    - contrasena_confirmacion: Confirmación de la nueva contraseña
    """
    
    contrasena_actual = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Contraseña actual del usuario"
    )
    
    contrasena_nueva = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        min_length=8,  # Requisito mínimo de seguridad
        help_text="Nueva contraseña (mínimo 8 caracteres)"
    )
    
    contrasena_confirmacion = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirmación de la nueva contraseña"
    )
    
    def validate_contrasena_nueva(self, value):
        """
        Validación de fortaleza de contraseña.
        
        Requisitos básicos:
        - Mínimo 8 caracteres (ya validado por min_length)
        - Al menos una letra
        - Al menos un número
        
        Args:
            value (str): Nueva contraseña
            
        Returns:
            str: Contraseña validada
            
        Raises:
            ValidationError: Si no cumple requisitos
        """
        # Validar que contenga al menos una letra
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos una letra"
            )
        
        # Validar que contenga al menos un número
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos un número"
            )
        
        return value
    
    def validate(self, data):
        """
        Validación cruzada de campos.
        
        Verifica que la nueva contraseña y su confirmación coincidan.
        
        Args:
            data (dict): Diccionario con todos los campos
            
        Returns:
            dict: Datos validados
            
        Raises:
            ValidationError: Si las contraseñas no coinciden
        """
        if data['contrasena_nueva'] != data['contrasena_confirmacion']:
            raise serializers.ValidationError({
                'contrasena_confirmacion': 'Las contraseñas no coinciden'
            })
        
        return data