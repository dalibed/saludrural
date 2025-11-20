"""
Views para el módulo de Notificaciones

Gestiona las notificaciones para pacientes y médicos.
Con PERMISOS implementados para proteger privacidad.

Lógica de permisos:
- Listar notificaciones: Usuario ve solo sus propias notificaciones
- Crear notificaciones: Sistema automático (no hay endpoint público)
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import DatabaseError

from .services import (
    sp_notificacion_list_paciente,
    sp_notificacion_list_medico
)


class NotificacionViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Notificaciones.
    
    Endpoints:
    - GET /api/notificaciones/paciente/:id_usuario/  → Notificaciones del paciente
    - GET /api/notificaciones/medico/:id_usuario/    → Notificaciones del médico
    
    Permisos:
    - list_paciente/list_medico: Autenticado + ownership (solo sus notificaciones)
    
    NOTA: Las notificaciones se crean automáticamente por el sistema
          cuando ocurren eventos (citas creadas, documentos validados, etc.)
    """
    
    def get_permissions(self):
        """
        Todos los endpoints requieren autenticación.
        Validación de ownership se hace en cada método.
        """
        return [IsAuthenticated()]
    
    # =========================================================================
    # ENDPOINTS DE LECTURA (Con ownership validation)
    # =========================================================================
    
    @action(detail=True, methods=['get'], url_path='paciente')
    def list_paciente(self, request, pk=None):
        """
        GET /api/notificaciones/paciente/:id_usuario/
        
        Lista las notificaciones de un paciente.
        
        Permiso: Autenticado
        
        Validación: Paciente solo ve sus propias notificaciones
        
        Args:
            pk: ID del usuario paciente
        
        Response:
            200: Lista de notificaciones
            403: No tiene permiso (no es su ID)
            404: Paciente no encontrado
        """
        id_usuario_paciente = int(pk)
        
        # VALIDACIÓN DE OWNERSHIP: Paciente solo ve sus notificaciones
        if request.user.rol == 'Paciente':
            from pacientes.models import Paciente
            try:
                paciente = Paciente.objects.get(id_usuario=request.user.id_usuario)
                
                # Verificar que esté consultando sus propias notificaciones
                if paciente.id_usuario != id_usuario_paciente:
                    return Response(
                        {
                            "detail": "No tienes permiso para ver las notificaciones de otros pacientes.",
                            "hint": "Solo puedes ver tus propias notificaciones."
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Paciente.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Admin puede ver notificaciones de cualquier paciente
        try:
            data = sp_notificacion_list_paciente(id_usuario_paciente)
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "paciente no existe" in msg:
                return Response(
                    {"detail": "El paciente no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='medico')
    def list_medico(self, request, pk=None):
        """
        GET /api/notificaciones/medico/:id_usuario/
        
        Lista las notificaciones de un médico.
        
        Permiso: Autenticado
        
        Validación: Médico solo ve sus propias notificaciones
        
        Args:
            pk: ID del usuario médico
        
        Response:
            200: Lista de notificaciones
            403: No tiene permiso (no es su ID)
            404: Médico no encontrado
        """
        id_usuario_medico = int(pk)
        
        # VALIDACIÓN DE OWNERSHIP: Médico solo ve sus notificaciones
        if request.user.rol == 'Medico':
            from medicos.models import Medico
            try:
                medico = Medico.objects.get(id_usuario=request.user.id_usuario)
                
                # Verificar que esté consultando sus propias notificaciones
                if medico.id_usuario.id_usuario != id_usuario_medico:
                    return Response(
                        {
                            "detail": "No tienes permiso para ver las notificaciones de otros médicos.",
                            "hint": "Solo puedes ver tus propias notificaciones."
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Medico.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Admin puede ver notificaciones de cualquier médico
        try:
            data = sp_notificacion_list_medico(id_usuario_medico)
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "médico no existe" in msg:
                return Response(
                    {"detail": "El médico no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(data, status=status.HTTP_200_OK)


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - list_paciente: IsAuthenticated + ownership (solo sus notificaciones)
#    - list_medico: IsAuthenticated + ownership (solo sus notificaciones)
#
# 2. CREACIÓN AUTOMÁTICA:
#    - Las notificaciones se crean mediante triggers en la BD
#    - Eventos que generan notificaciones:
#      * Cita creada → Notifica a médico
#      * Cita confirmada → Notifica a paciente
#      * Cita cancelada → Notifica a ambos
#      * Documento validado → Notifica a médico
#      * Entrada médica creada → Notifica a paciente
#
# 3. TIPOS DE NOTIFICACIONES:
#    - Información: "Tu cita ha sido confirmada"
#    - Recordatorio: "Tienes una cita mañana a las 10:00"
#    - Alerta: "Tu documento fue rechazado"
#    - Confirmación: "Tu cuenta ha sido aprobada"
#
# 4. CAMPOS TÍPICOS:
#    - Mensaje: Texto de la notificación
#    - Fecha: Cuándo se generó
#    - Leída: Si el usuario ya la vio
#    - Tipo: Categoría de la notificación
#
# 5. FUTURAS MEJORAS:
#    - Marcar como leída (PUT /notificaciones/:id/leer/)
#    - Eliminar notificación (DELETE /notificaciones/:id/)
#    - Notificaciones push (WebSockets)
#    - Preferencias de notificación por usuario
#
# =============================================================================