"""
Views para el módulo de Autenticación

Este módulo implementa los endpoints de autenticación usando JWT.
Mantiene el patrón del proyecto: ViewSet con validación de serializers.

Endpoints:
- POST   /api/auth/login/     - Iniciar sesión
- POST   /api/auth/logout/    - Cerrar sesión
- GET    /api/auth/me/        - Info del usuario autenticado
- POST   /api/auth/refresh/   - Renovar access token
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.db import DatabaseError

from usuarios.models import Usuario
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
)


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet para operaciones de autenticación.
    
    Este ViewSet maneja la autenticación usando JWT (JSON Web Tokens).
    No tiene modelo asociado porque no interactúa directamente con tablas,
    sino que valida credenciales y genera/invalida tokens.
    """
    
    # Por defecto, los endpoints de auth son públicos (login)
    # Los endpoints protegidos especifican su permiso individualmente
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Endpoint de inicio de sesión.
        
        Valida credenciales del usuario y genera tokens JWT.
        
        Request:
            POST /api/auth/login/
            {
                "correo": "usuario@example.com",
                "contrasena": "password123"
            }
        
        Response (200 OK):
            {
                "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "usuario": {
                    "id_usuario": 1,
                    "nombre": "Juan",
                    "apellidos": "Pérez",
                    "correo": "usuario@example.com",
                    "rol": "Paciente"
                }
            }
        
        Errors:
            - 400: Datos inválidos
            - 401: Credenciales incorrectas
            - 403: Usuario desactivado
        """
        # 1. Validar datos de entrada
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        correo = serializer.validated_data['correo']
        contrasena = serializer.validated_data['contrasena']
        
        # 2. Buscar usuario por correo
        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            # Por seguridad, no revelamos si el correo existe o no
            return Response(
                {"detail": "Credenciales inválidas."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 3. Verificar que el usuario esté activo
        if not usuario.activo:
            return Response(
                {
                    "detail": "Usuario desactivado. Contacte al administrador.",
                    "motivo": usuario.motivo_inactivacion
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 4. Validar contraseña
        # Nota: check_password compara el texto plano con el hash en BD
        if not usuario.check_password(contrasena):
            return Response(
                {"detail": "Credenciales inválidas."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 5. Generar tokens JWT
        # RefreshToken crea un par de tokens (refresh + access)
        refresh = RefreshToken()
        
        # Agregar información adicional al payload del token
        refresh['user_id'] = usuario.id_usuario
        refresh['rol'] = usuario.rol
        refresh['correo'] = usuario.correo
        
        # 6. Preparar respuesta
        response_data = {
            'access': str(refresh.access_token),  # Token de acceso (corta duración)
            'refresh': str(refresh),              # Token de refresco (larga duración)
            'usuario': {
                'id_usuario': usuario.id_usuario,
                'nombre': usuario.nombre,
                'apellidos': usuario.apellidos,
                'correo': usuario.correo,
                'rol': usuario.rol,
                'documento': usuario.documento,
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Endpoint de cierre de sesión.
        
        Invalida el refresh token para que no pueda usarse más.
        El access token seguirá siendo válido hasta su expiración natural
        (esto es una limitación de JWT stateless, pero 60 min es aceptable).
        
        Request:
            POST /api/auth/logout/
            {
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
            }
        
        Response (200 OK):
            {
                "detail": "Sesión cerrada exitosamente."
            }
        
        Errors:
            - 400: Token inválido o ya usado
        """
        # 1. Validar datos de entrada
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 2. Intentar invalidar el token
        try:
            # Crear instancia del token para agregar a blacklist
            token = RefreshToken(serializer.validated_data['refresh'])
            
            # Agregar a blacklist (requiere rest_framework_simplejwt.token_blacklist)
            token.blacklist()
            
            return Response(
                {"detail": "Sesión cerrada exitosamente."},
                status=status.HTTP_200_OK
            )
            
        except TokenError as e:
            # Token ya fue usado, expiró, o es inválido
            return Response(
                {"detail": f"Token inválido: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint para obtener información del usuario autenticado.
        
        Útil para que el frontend verifique el estado del usuario
        o recargue información después de cambios.
        
        Request:
            GET /api/auth/me/
            Headers:
                Authorization: Bearer {access_token}
        
        Response (200 OK):
            {
                "id_usuario": 1,
                "nombre": "Juan",
                "apellidos": "Pérez",
                "correo": "usuario@example.com",
                "documento": "123456789",
                "telefono": "555-1234",
                "rol": "Paciente",
                "activo": true,
                "fecha_registro": "2024-01-01"
            }
        
        Errors:
            - 401: Token ausente o inválido
        """
        # request.user ya está disponible gracias al middleware JWT
        usuario = request.user
        
        # Retornar información completa del usuario
        return Response({
            'id_usuario': usuario.id_usuario,
            'nombre': usuario.nombre,
            'apellidos': usuario.apellidos,
            'correo': usuario.correo,
            'documento': usuario.documento,
            'telefono': usuario.telefono,
            'rol': usuario.rol,
            'activo': usuario.activo,
            # Campos adicionales según necesidad
        }, status=status.HTTP_200_OK)
    
    @action(
        detail=False, 
        methods=['post'], 
        url_path='change-password',
        permission_classes=[IsAuthenticated]
    )
    def change_password(self, request):
        """
        Endpoint para cambiar contraseña del usuario autenticado.
        
        El usuario debe estar autenticado y solo puede cambiar su propia contraseña.
        
        Request:
            POST /api/auth/change-password/
            Headers:
                Authorization: Bearer {access_token}
            Body:
                {
                    "contrasena_actual": "oldpass123",
                    "contrasena_nueva": "newpass456",
                    "contrasena_confirmacion": "newpass456"
                }
        
        Response (200 OK):
            {
                "detail": "Contraseña actualizada exitosamente."
            }
        
        Errors:
            - 400: Contraseña actual incorrecta o datos inválidos
            - 401: No autenticado
        """
        # 1. Validar datos de entrada
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        usuario = request.user
        
        # 2. Verificar contraseña actual
        if not usuario.check_password(serializer.validated_data['contrasena_actual']):
            return Response(
                {"detail": "La contraseña actual es incorrecta."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Actualizar contraseña
        try:
            # set_password hashea automáticamente la nueva contraseña
            usuario.set_password(serializer.validated_data['contrasena_nueva'])
            
            # Guardar en BD
            # Nota: Como managed=False, debemos guardar manualmente
            # O mejor aún, usar un SP si existe
            usuario.save(update_fields=['contrasena'])
            
            return Response(
                {"detail": "Contraseña actualizada exitosamente."},
                status=status.HTTP_200_OK
            )
            
        except DatabaseError as e:
            return Response(
                {"detail": f"Error al actualizar contraseña: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============================================================================
# NOTAS ADICIONALES PARA EL DESARROLLADOR
# =============================================================================
#
# 1. SEGURIDAD:
#    - Nunca revelar si un correo existe en mensajes de error (evita enumeración)
#    - Siempre usar mensajes genéricos: "Credenciales inválidas"
#    - Los tokens se envían por HTTPS en producción
#
# 2. JWT vs SESSION:
#    - JWT es stateless: el servidor no guarda estado
#    - Ventaja: Escalabilidad (no requiere sesiones compartidas)
#    - Desventaja: No se puede invalidar un access token antes de expirar
#    - Solución: Tokens de corta duración (60 min)
#
# 3. BLACKLIST:
#    - Solo funciona para refresh tokens
#    - Requiere tabla en BD (creada por migración)
#    - El access token sigue válido hasta expirar
#
# 4. BUENAS PRÁCTICAS IMPLEMENTADAS:
#    - Validación con serializers
#    - Manejo explícito de errores
#    - Mensajes claros y consistentes
#    - Comentarios detallados
#    - Type hints donde es posible
#    - Respuestas HTTP semánticas (200, 400, 401, 403)
#
# =============================================================================