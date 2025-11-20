"""
Views para el módulo de Usuarios

Este módulo maneja todas las operaciones CRUD de usuarios.
Ahora con PERMISOS implementados para proteger la información.

Lógica de permisos:
- Registro (create): Público - Cualquiera puede registrarse
- Listar (list): Solo Administradores
- Ver detalle (retrieve): Usuario ve solo su info, Admin ve todo
- Actualizar (update): Usuario actualiza solo su info, Admin actualiza todo
- Desactivar (destroy): Solo Administradores
- Activar (activate): Solo Administradores
"""

from django.db import DatabaseError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

# Importar permisos personalizados
from backend.permissions import IsAdministrador

from .serializers import (
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
)
from .services import (
    sp_usuario_create,
    sp_usuario_update,
    sp_usuario_get,
    sp_usuario_list,
    sp_usuario_deactivate,
    sp_usuario_activate,
)


class UsuarioViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Usuarios.
    
    Endpoints:
    - POST   /api/usuarios/              → Registro (público)
    - GET    /api/usuarios/              → Listar todos (solo admin)
    - GET    /api/usuarios/:id/          → Ver uno (propio o admin)
    - PUT    /api/usuarios/:id/          → Actualizar (propio o admin)
    - DELETE /api/usuarios/:id/          → Desactivar (solo admin)
    - POST   /api/usuarios/:id/activar/  → Activar (solo admin)
    
    Permisos implementados:
    - create: Público (AllowAny)
    - list: Solo Administradores
    - retrieve: Usuario autenticado ve solo su info, Admin ve cualquiera
    - update: Usuario actualiza solo su info, Admin actualiza cualquiera
    - destroy: Solo Administradores
    - activate: Solo Administradores
    """
    
    def get_permissions(self):
        """
        Define los permisos según la acción.
        
        Lógica:
        - create (registro): Sin autenticación requerida
        - list: Solo administradores
        - destroy/activate: Solo administradores
        - retrieve/update: Usuario autenticado (validación en el método)
        
        Returns:
            list: Lista de instancias de permisos
        """
        if self.action == 'create':
            # Registro es público
            return [AllowAny()]
        
        elif self.action == 'list':
            # Solo administradores pueden listar todos los usuarios
            return [IsAdministrador()]
        
        elif self.action in ['destroy', 'activate']:
            # Solo administradores pueden activar/desactivar usuarios
            return [IsAdministrador()]
        
        else:
            # retrieve, update: Usuario autenticado
            # La validación de ownership se hace en cada método
            return [IsAuthenticated()]
    
    # =========================================================================
    # ENDPOINTS CRUD
    # =========================================================================
    
    def list(self, request):
        """
        GET /api/usuarios/
        
        Lista todos los usuarios del sistema.
        
        Permiso: Solo Administradores
        
        Response:
            200: Lista de usuarios
        """
        data = sp_usuario_list()
        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """
        GET /api/usuarios/:id/
        
        Obtiene la información de un usuario específico.
        
        Permiso: 
        - Usuario puede ver solo su propia información
        - Administrador puede ver cualquier usuario
        
        Args:
            pk: ID del usuario a consultar
            
        Response:
            200: Datos del usuario
            403: No tiene permiso para ver este usuario
            404: Usuario no encontrado
        """
        # Validar ownership: Usuario solo puede ver su propia información
        if request.user.rol != 'Administrador':
            if request.user.id_usuario != int(pk):
                return Response(
                    {
                        "detail": "No tienes permiso para ver la información de otros usuarios.",
                        "hint": "Solo puedes ver tu propia información."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Obtener usuario
        usuario = sp_usuario_get(int(pk))
        
        if not usuario:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(usuario, status=status.HTTP_200_OK)
    
    def create(self, request):
        """
        POST /api/usuarios/
        
        Registra un nuevo usuario en el sistema.
        
        Permiso: Público (sin autenticación)
        
        Request Body:
            {
                "nombre": "Juan",
                "apellidos": "Pérez",
                "documento": "123456789",
                "correo": "juan@example.com",
                "contrasena": "password123",
                "telefono": "555-1234",
                "rol": "Paciente",
                "fecha_nacimiento": "1990-01-01"  // Opcional
            }
        
        Response:
            201: Usuario creado exitosamente
            400: Datos inválidos o duplicados
        """
        # Validar datos de entrada
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Crear usuario mediante stored procedure
            nuevo_id = sp_usuario_create(**serializer.validated_data)
            
        except DatabaseError as e:
            # Manejar errores específicos del stored procedure
            msg = str(e).lower()
            
            if "documento duplicado" in msg:
                return Response(
                    {
                        "detail": "El documento ya está registrado.",
                        "field": "documento"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "correo duplicado" in msg:
                return Response(
                    {
                        "detail": "El correo ya está registrado.",
                        "field": "correo"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "formato de correo inválido" in msg:
                return Response(
                    {
                        "detail": "El formato del correo es inválido.",
                        "field": "correo"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cualquier otro error del stored procedure
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener y retornar el usuario creado
        usuario = sp_usuario_get(nuevo_id)
        return Response(usuario, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """
        PUT /api/usuarios/:id/
        
        Actualiza la información de un usuario.
        
        Permiso:
        - Usuario puede actualizar solo su propia información
        - Administrador puede actualizar cualquier usuario
        
        Args:
            pk: ID del usuario a actualizar
        
        Request Body:
            {
                "nombre": "Juan",
                "apellidos": "Pérez García",
                "correo": "juan.nuevo@example.com",
                "telefono": "555-5678"
            }
        
        Response:
            200: Usuario actualizado
            403: No tiene permiso para modificar este usuario
            404: Usuario no encontrado
            400: Datos inválidos
        """
        # Validar ownership: Usuario solo puede actualizar su propia información
        if request.user.rol != 'Administrador':
            if request.user.id_usuario != int(pk):
                return Response(
                    {
                        "detail": "No tienes permiso para modificar la información de otros usuarios.",
                        "hint": "Solo puedes modificar tu propia información."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validar datos de entrada
        serializer = UsuarioUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Actualizar mediante stored procedure
            sp_usuario_update(int(pk), **serializer.validated_data)
            
        except DatabaseError as e:
            # Manejar errores específicos
            msg = str(e).lower()
            
            if "no existe" in msg:
                return Response(
                    {"detail": "El usuario no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "desactivado" in msg:
                return Response(
                    {
                        "detail": "El usuario está desactivado. No se permiten cambios.",
                        "hint": "Contacte al administrador para reactivar el usuario."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "correo ya está en uso" in msg or "correo ya está en uso por otro usuario" in msg:
                return Response(
                    {
                        "detail": "El correo ya está en uso por otro usuario.",
                        "field": "correo"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener y retornar el usuario actualizado
        usuario = sp_usuario_get(int(pk))
        return Response(usuario, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        """
        DELETE /api/usuarios/:id/
        
        Desactiva un usuario del sistema (soft delete).
        
        Permiso: Solo Administradores
        
        Args:
            pk: ID del usuario a desactivar
        
        Request Body (opcional):
            {
                "motivo": "Motivo de la desactivación"
            }
        
        Response:
            200: Usuario desactivado
            404: Usuario no encontrado
            400: Error al desactivar
        """
        # Obtener motivo de desactivación (opcional)
        motivo = request.data.get("motivo", "Desactivado por el administrador")
        
        try:
            # Desactivar usuario mediante stored procedure
            sp_usuario_deactivate(int(pk), motivo)
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no existe" in msg:
                return Response(
                    {"detail": "El usuario no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": "Usuario desactivado exitosamente.",
                "motivo": motivo
            },
            status=status.HTTP_200_OK
        )
    
    # =========================================================================
    # ENDPOINTS ADICIONALES
    # =========================================================================
    
    @action(detail=True, methods=['post'], url_path='activar')
    def activate(self, request, pk=None):
        """
        POST /api/usuarios/:id/activar/
        
        Reactiva un usuario previamente desactivado.
        
        Permiso: Solo Administradores
        
        Args:
            pk: ID del usuario a activar
        
        Response:
            200: Usuario activado
            404: Usuario no encontrado
            400: Error al activar
        """
        try:
            # Activar usuario mediante stored procedure
            sp_usuario_activate(int(pk))
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no existe" in msg:
                return Response(
                    {"detail": "El usuario no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {"detail": "Usuario activado exitosamente."},
            status=status.HTTP_200_OK
        )


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - create: AllowAny (registro público)
#    - list: IsAdministrador
#    - retrieve/update: IsAuthenticated + validación de ownership
#    - destroy/activate: IsAdministrador
#
# 2. VALIDACIÓN DE OWNERSHIP:
#    En retrieve() y update():
#    - Si rol != 'Administrador'
#    - Verifica que request.user.id_usuario == pk
#    - Si no coincide → 403 Forbidden
#
# 3. MENSAJES DE ERROR:
#    - Claros y útiles
#    - Incluyen "hint" cuando es relevante
#    - No revelan información sensible
#
# 4. STORED PROCEDURES:
#    - No se modifican, siguen funcionando igual
#    - Los permisos se validan ANTES de llamar al SP
#
# 5. TESTING:
#    - Probar con diferentes roles
#    - Probar ownership (intentar acceder a ID ajeno)
#    - Probar sin token (debe dar 401)
#
# =============================================================================