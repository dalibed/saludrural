"""
Views para el módulo de Videollamada

Gestiona enlaces de videollamada para teleconsultas.
Con PERMISOS implementados para proteger privacidad.

Lógica de permisos:
- Crear enlace: Solo el médico de la cita
- Ver enlace: Solo médico o paciente involucrados en la cita
"""

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import DatabaseError

from backend.permissions import IsMedico

from .services import (
    sp_videollamada_crear,
    sp_videollamada_get
)


class VideollamadaViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Videollamadas.
    
    Endpoints:
    - POST /api/videollamada/:id_cita/  → Crear enlace (médico de la cita)
    - GET  /api/videollamada/:id_cita/  → Ver enlace (involucrados en la cita)
    
    Permisos:
    - crear: Solo el médico asignado a la cita
    - retrieve: Solo médico o paciente de la cita
    
    Uso: Teleconsulta mediante videollamada (Zoom, Google Meet, etc.)
    """
    
    def get_permissions(self):
        """
        Define permisos según la acción.
        
        - crear: Solo Médicos (validación adicional en el método)
        - retrieve: Autenticado (validación adicional en el método)
        """
        if self.action == 'crear':
            return [IsMedico()]
        return [IsAuthenticated()]
    
    # =========================================================================
    # ENDPOINTS DE ESCRITURA
    # =========================================================================
    
    def crear(self, request, pk=None):
        """
        POST /api/videollamada/:id_cita/
        
        Crea o actualiza el enlace de videollamada para una cita.
        
        Permiso: Solo el médico asignado a la cita
        
        Args:
            pk: ID de la cita
        
        Request Body:
            {
                "enlace": "https://zoom.us/j/123456789"
            }
        
        Response:
            200: Enlace creado/actualizado
            400: Falta enlace o datos inválidos
            403: No es el médico de la cita
            404: Cita no encontrada
        
        VALIDACIÓN: El stored procedure debe validar que el médico
                    autenticado es el asignado a la cita.
        """
        enlace = request.data.get("enlace")
        
        if not enlace:
            return Response(
                {
                    "detail": "Debe proporcionar un enlace de videollamada.",
                    "hint": "Ejemplos: Zoom, Google Meet, Microsoft Teams"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el médico está asignado a esta cita
        from citas.models import Cita
        try:
            cita = Cita.objects.get(id_cita=int(pk))
            
            # Verificar que el médico autenticado es el asignado a la cita
            if cita.id_usuario_medico.id_usuario != request.user.id_usuario:
                return Response(
                    {
                        "detail": "Solo el médico asignado a la cita puede crear el enlace.",
                        "hint": "Esta cita no te fue asignada."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except Cita.DoesNotExist:
            return Response(
                {"detail": "La cita no existe."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            mensaje = sp_videollamada_crear(
                int(pk),
                enlace
            )
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "cita no existe" in msg:
                return Response(
                    {"detail": "La cita no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": mensaje,
                "enlace": enlace
            },
            status=status.HTTP_200_OK
        )
    
    # =========================================================================
    # ENDPOINTS DE LECTURA
    # =========================================================================
    
    def retrieve(self, request, pk=None):
        """
        GET /api/videollamada/:id_cita/
        
        Obtiene el enlace de videollamada para una cita.
        
        Permiso: Solo médico o paciente involucrados en la cita
        
        Args:
            pk: ID de la cita
        
        Response:
            200: Enlace de videollamada
            403: No es participante de la cita
            404: Cita o enlace no encontrado
        """
        # VALIDACIÓN DE OWNERSHIP: Solo involucrados en la cita
        from citas.models import Cita
        try:
            cita = Cita.objects.get(id_cita=int(pk))
            
            # Verificar que el usuario es médico o paciente de esta cita
            es_medico_cita = (request.user.rol == 'Medico' and 
                            cita.id_usuario_medico.id_usuario == request.user.id_usuario)
            
            es_paciente_cita = (request.user.rol == 'Paciente' and 
                            cita.id_usuario_paciente.id_usuario == request.user.id_usuario)
            
            es_admin = request.user.rol == 'Administrador'
            
            if not (es_medico_cita or es_paciente_cita or es_admin):
                return Response(
                    {
                        "detail": "No tienes permiso para ver este enlace.",
                        "hint": "Solo los participantes de la cita pueden acceder al enlace."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
                
        except Cita.DoesNotExist:
            return Response(
                {"detail": "La cita no existe."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            data = sp_videollamada_get(int(pk))
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "cita no existe" in msg:
                return Response(
                    {"detail": "La cita no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data:
            return Response(
                {
                    "detail": "La videollamada no está configurada para esta cita.",
                    "hint": "El médico debe crear el enlace primero."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(data, status=status.HTTP_200_OK)


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - crear: IsMedico + validación que sea el médico de la cita
#    - retrieve: IsAuthenticated + validación de participación en la cita
#
# 2. VALIDACIÓN DE OWNERSHIP:
#    - Solo médico de la cita puede crear enlace
#    - Solo médico/paciente de la cita pueden ver enlace
#    - Admin puede ver todos los enlaces
#
# 3. USO TÍPICO:
#    a) Médico crea cita presencial o virtual
#    b) Si es virtual, médico crea enlace de videollamada
#    c) Paciente accede al enlace para unirse a la consulta
#    d) Ambos se conectan en el horario acordado
#
# 4. PLATAFORMAS SOPORTADAS:
#    - Zoom
#    - Google Meet
#    - Microsoft Teams
#    - Jitsi Meet
#    - Cualquier plataforma con enlace directo
#
# 5. SEGURIDAD:
#    - Enlaces solo visibles para participantes
#    - No se pueden ver enlaces de citas ajenas
#    - Enlaces temporales (válidos solo durante la cita)
#
# 6. MEJORAS FUTURAS:
#    - Integración directa con APIs de Zoom/Meet
#    - Generación automática de enlaces
#    - Grabación de consultas (con consentimiento)
#    - Chat durante videollamada
#    - Compartir pantalla para ver estudios
#
# =============================================================================