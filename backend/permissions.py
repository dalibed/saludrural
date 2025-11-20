"""
Permisos Personalizados - Salud Rural

Este módulo define clases de permisos reutilizables para controlar el acceso
a los recursos del sistema según el rol del usuario.

Jerarquía de permisos:
1. IsAuthenticated - Usuario debe estar autenticado (base)
2. Rol específico - IsPaciente, IsMedico, IsAdministrador
3. Ownership - Solo puede acceder a sus propios recursos

Uso en ViewSets:
    from backend.permisos import IsPaciente, IsOwner
    
    class MiViewSet(viewsets.ViewSet):
        permission_classes = [IsPaciente, IsOwner]

Autor: Equipo Salud Rural
Fecha: 2024
"""

from rest_framework import permissions


# =============================================================================
# PERMISOS BASE
# =============================================================================

class IsAuthenticated(permissions.BasePermission):
    """
    Permiso base: Usuario debe estar autenticado.
    
    Verifica que el request tenga un usuario válido y autenticado.
    Se usa como base para otros permisos más específicos.
    
    Uso:
        permission_classes = [IsAuthenticated]
        
    Ejemplo de error:
        HTTP 401 Unauthorized
        {"detail": "Las credenciales de autenticación no se proveyeron."}
    """
    
    message = "Debe estar autenticado para realizar esta acción."
    
    def has_permission(self, request, view):
        """
        Verifica que el usuario esté autenticado.
        
        Args:
            request: HttpRequest con información del usuario
            view: View que está siendo accedida
            
        Returns:
            bool: True si está autenticado, False si no
        """
        return bool(
            request.user and 
            request.user.is_authenticated
        )


# =============================================================================
# PERMISOS POR ROL
# =============================================================================

class IsPaciente(permissions.BasePermission):
    """
    Permiso: Solo usuarios con rol 'Paciente' pueden acceder.
    
    Verifica que el usuario autenticado tenga rol='Paciente'.
    Implícitamente requiere autenticación.
    
    Uso:
        permission_classes = [IsPaciente]
        
    Casos de uso:
        - Crear citas
        - Ver propia historia clínica
        - Cancelar propias citas
    """
    
    message = "Solo los pacientes pueden realizar esta acción."
    
    def has_permission(self, request, view):
        """
        Verifica que el usuario sea un paciente autenticado.
        
        Args:
            request: HttpRequest con información del usuario
            view: View que está siendo accedida
            
        Returns:
            bool: True si es paciente, False si no
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol == 'Paciente'
        )


class IsMedico(permissions.BasePermission):
    """
    Permiso: Solo usuarios con rol 'Medico' pueden acceder.
    
    Verifica que el usuario autenticado tenga rol='Medico'.
    
    Uso:
        permission_classes = [IsMedico]
        
    Casos de uso:
        - Crear/modificar agenda
        - Completar citas
        - Actualizar historias clínicas
        - Subir documentos de validación
    """
    
    message = "Solo los médicos pueden realizar esta acción."
    
    def has_permission(self, request, view):
        """
        Verifica que el usuario sea un médico autenticado.
        
        Args:
            request: HttpRequest con información del usuario
            view: View que está siendo accedida
            
        Returns:
            bool: True si es médico, False si no
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol == 'Medico'
        )


class IsAdministrador(permissions.BasePermission):
    """
    Permiso: Solo usuarios con rol 'Administrador' pueden acceder.
    
    Verifica que el usuario autenticado tenga rol='Administrador'.
    Los administradores tienen acceso privilegiado al sistema.
    
    Uso:
        permission_classes = [IsAdministrador]
        
    Casos de uso:
        - Listar todos los usuarios
        - Validar documentos de médicos
        - Activar/desactivar usuarios
        - Gestionar tipos de documentos
        - Gestionar diccionario médico
    """
    
    message = "Solo los administradores pueden realizar esta acción."
    
    def has_permission(self, request, view):
        """
        Verifica que el usuario sea un administrador autenticado.
        
        Args:
            request: HttpRequest con información del usuario
            view: View que está siendo accedida
            
        Returns:
            bool: True si es administrador, False si no
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol == 'Administrador'
        )


# =============================================================================
# PERMISOS COMBINADOS
# =============================================================================

class IsMedicoOrAdministrador(permissions.BasePermission):
    """
    Permiso: Médicos O Administradores pueden acceder.
    
    Útil para recursos que deben ser accesibles por personal médico
    y administrativo, pero no por pacientes.
    
    Uso:
        permission_classes = [IsMedicoOrAdministrador]
        
    Casos de uso:
        - Ver historias clínicas completas
        - Acceder a reportes médicos
        - Gestionar entradas de historia
    """
    
    message = "Solo médicos o administradores pueden realizar esta acción."
    
    def has_permission(self, request, view):
        """
        Verifica que el usuario sea médico o administrador.
        
        Args:
            request: HttpRequest con información del usuario
            view: View que está siendo accedida
            
        Returns:
            bool: True si es médico o admin, False si no
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol in ['Medico', 'Administrador']
        )


# =============================================================================
# PERMISOS DE OWNERSHIP (PROPIETARIO)
# =============================================================================

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso: El usuario puede acceder solo a sus propios recursos,
    o ser administrador (acceso total).
    
    Verifica ownership a nivel de objeto individual.
    Se usa en métodos retrieve, update, delete.
    
    Uso:
        permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        
    Importante:
        - has_permission() verifica autenticación
        - has_object_permission() verifica ownership
    
    Casos de uso:
        - Usuario ve su propio perfil
        - Usuario edita sus propios datos
        - Admin puede ver/editar cualquier usuario
    """
    
    message = "Solo puedes acceder a tu propia información o ser administrador."
    
    def has_permission(self, request, view):
        """
        Verificación a nivel de vista (antes de obtener el objeto).
        
        Args:
            request: HttpRequest con información del usuario
            view: View que está siendo accedida
            
        Returns:
            bool: True si está autenticado
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Verificación a nivel de objeto (después de obtener el objeto).
        
        Args:
            request: HttpRequest con información del usuario
            view: View que está siendo accedida
            obj: Objeto específico al que se intenta acceder
            
        Returns:
            bool: True si es dueño o admin, False si no
        """
        # Administradores tienen acceso total
        if hasattr(request.user, 'rol') and request.user.rol == 'Administrador':
            return True
        
        # Usuario solo puede acceder a sus propios datos
        # Intentamos diferentes formas de identificar ownership
        if hasattr(obj, 'id_usuario'):
            return obj.id_usuario == request.user.id_usuario
        
        # Para modelos que directamente son Usuario
        if hasattr(obj, 'id_usuario') and hasattr(obj, 'rol'):
            return obj.id_usuario == request.user.id_usuario
        
        return False


class IsPacienteOwner(permissions.BasePermission):
    """
    Permiso: El paciente solo puede acceder a sus propios recursos.
    
    Similar a IsOwnerOrAdmin pero específico para pacientes.
    No permite acceso a administradores por defecto.
    
    Uso:
        permission_classes = [IsPacienteOwner]
        
    Casos de uso:
        - Paciente ve sus propias citas
        - Paciente ve su propia historia clínica
    """
    
    message = "Solo puedes acceder a tu propia información como paciente."
    
    def has_permission(self, request, view):
        """Verifica que sea un paciente autenticado."""
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol == 'Paciente'
        )
    
    def has_object_permission(self, request, view, obj):
        """Verifica que el paciente accede a sus propios datos."""
        # Buscar el campo que identifica al paciente
        if hasattr(obj, 'id_usuario_paciente'):
            return obj.id_usuario_paciente == request.user.id_usuario
        elif hasattr(obj, 'id_usuario'):
            return obj.id_usuario == request.user.id_usuario
        
        return False


class IsMedicoOwner(permissions.BasePermission):
    """
    Permiso: El médico solo puede acceder a sus propios recursos.
    
    Específico para médicos. Útil para agenda, documentos, etc.
    
    Uso:
        permission_classes = [IsMedicoOwner]
        
    Casos de uso:
        - Médico ve su propia agenda
        - Médico ve sus propios documentos
        - Médico ve sus propias citas
    """
    
    message = "Solo puedes acceder a tu propia información como médico."
    
    def has_permission(self, request, view):
        """Verifica que sea un médico autenticado."""
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol == 'Medico'
        )
    
    def has_object_permission(self, request, view, obj):
        """Verifica que el médico accede a sus propios datos."""
        # Buscar el campo que identifica al médico
        if hasattr(obj, 'id_usuario_medico'):
            return obj.id_usuario_medico == request.user.id_usuario
        elif hasattr(obj, 'id_usuario'):
            return obj.id_usuario == request.user.id_usuario
        
        return False


# =============================================================================
# PERMISOS DE SOLO LECTURA
# =============================================================================

class ReadOnly(permissions.BasePermission):
    """
    Permiso: Solo operaciones de lectura (GET, HEAD, OPTIONS).
    
    Permite leer pero no modificar recursos.
    Se usa en combinación con otros permisos.
    
    Uso:
        permission_classes = [IsAuthenticated, ReadOnly]
        
    Casos de uso:
        - Pacientes ven agenda de médicos (solo lectura)
        - Usuarios ven diccionario médico (solo lectura)
    """
    
    message = "Solo tienes permisos de lectura en este recurso."
    
    def has_permission(self, request, view):
        """
        Verifica que sea un método seguro (lectura).
        
        Args:
            request: HttpRequest con información del método
            view: View que está siendo accedida
            
        Returns:
            bool: True si es método de lectura, False si no
        """
        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
        return request.method in permissions.SAFE_METHODS


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. USO EN VIEWSETS:
#    
#    # Permiso único para todo el ViewSet
#    class MiViewSet(viewsets.ViewSet):
#        permission_classes = [IsPaciente]
#    
#    # Permisos diferentes por acción
#    class MiViewSet(viewsets.ViewSet):
#        def get_permissions(self):
#            if self.action == 'create':
#                return [IsPaciente()]
#            elif self.action == 'list':
#                return [IsAdministrador()]
#            return [IsAuthenticated()]
#
# 2. VALIDACIÓN ADICIONAL EN VIEWS:
#    Los permisos validan a nivel general, pero a veces necesitas
#    validación adicional en la lógica de la view:
#    
#    def create(self, request):
#        # Permiso: IsPaciente
#        # Validación adicional:
#        if data['id_usuario_paciente'] != request.user.id_usuario:
#            return Response({"detail": "..."}, 403)
#
# 3. ORDEN DE EJECUCIÓN:
#    1. has_permission() - Verifica permiso general
#    2. View logic - Ejecuta lógica
#    3. has_object_permission() - Verifica permiso sobre objeto específico
#
# 4. TESTING:
#    Probar cada permiso con diferentes roles:
#    - Sin autenticación → 401
#    - Con rol incorrecto → 403
#    - Con ownership incorrecto → 403
#    - Con todo correcto → 200/201
#
# 5. MENSAJES DE ERROR:
#    Los mensajes deben ser claros pero no revelar información sensible:
#    - ✅ "Solo los médicos pueden realizar esta acción"
#    - ❌ "El médico con ID 123 no tiene permiso"
#
# =============================================================================