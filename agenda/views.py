"""
Views para el módulo de Agenda

Este módulo maneja la disponibilidad de horarios de los médicos.
Ahora con PERMISOS implementados para controlar el acceso.

Lógica de permisos:
- Crear agenda (create): Solo Médicos
- Ver agenda completa (retrieve): Público (pacientes necesitan ver disponibilidad)
- Ver solo disponibles (disponible): Público
- Toggle disponibilidad (toggle): Solo el médico dueño de la agenda
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import DatabaseError

# Importar permisos personalizados
from backend.permissions import IsMedico

from .serializers import (
    AgendaCreateRangeSerializer,
    AgendaToggleSerializer,
    AgendaSerializer
)
from .services import (
    sp_agenda_create_range,
    sp_agenda_toggle_slot,
    sp_agenda_list_by_usuario,
    sp_agenda_list_disponible_by_usuario
)


class AgendaViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Agenda de Médicos.
    
    Endpoints:
    - POST   /api/agendas/                    → Crear slots de agenda (solo médico)
    - GET    /api/agendas/:id_medico/         → Ver agenda completa (público)
    - GET    /api/agendas/disponible/:id/     → Ver solo slots disponibles (público)
    - PUT    /api/agendas/toggle/:id_agenda/  → Activar/desactivar slot (solo dueño)
    
    Permisos implementados:
    - create: Solo Médicos (IsMedico)
    - retrieve: Público (AllowAny) - Pacientes necesitan ver disponibilidad
    - disponible: Público (AllowAny) - Para reservar citas
    - toggle: Autenticado + validación de ownership
    """
    
    def get_permissions(self):
        """
        Define los permisos según la acción.
        
        Lógica:
        - create: Solo médicos pueden crear su agenda
        - retrieve/disponible: Público (pacientes ven disponibilidad)
        - toggle: Autenticado (validación de ownership en el método)
        
        Returns:
            list: Lista de instancias de permisos
        """
        if self.action == 'create':
            # Solo médicos crean agenda
            return [IsMedico()]
        
        elif self.action in ['retrieve', 'disponible']:
            # Lectura pública: pacientes necesitan ver horarios disponibles
            return [AllowAny()]
        
        else:
            # toggle: Médico autenticado (ownership validado en el método)
            return [IsAuthenticated()]
    
    # =========================================================================
    # ENDPOINTS CRUD
    # =========================================================================
    
    def create(self, request):
        """
        POST /api/agendas/
        
        Crea múltiples slots de agenda para un médico en un rango de horas.
        
        Permiso: Solo Médicos
        
        Validaciones adicionales:
        - Solo puede crear agenda para sí mismo
        - Debe estar validado y con documentos aprobados
        - No puede crear en fechas pasadas
        - Horarios entre 06:00 y 22:00
        
        Request Body:
            {
                "id_usuario_medico": 2,
                "fecha": "2025-12-01",
                "hora_inicio": "08:00",
                "hora_fin": "12:00"
            }
        
        Response:
            201: Slots creados
            400: Datos inválidos
            403: Médico no validado o desactivado
            404: Usuario no es médico
        """
        serializer = AgendaCreateRangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        id_usuario_medico = serializer.validated_data["id_usuario_medico"]
        
        # VALIDACIÓN DE OWNERSHIP: Médico solo puede crear su propia agenda
        if request.user.rol == 'Medico':
            # Obtener el ID_Medico del usuario autenticado
            from medicos.models import Medico
            try:
                medico = Medico.objects.get(id_usuario=request.user.id_usuario)
                
                # Verificar que el médico esté creando su propia agenda
                if medico.id_usuario != id_usuario_medico:
                    return Response(
                        {
                            "detail": "Solo puedes crear agenda para ti mismo.",
                            "hint": f"Tu ID de usuario médico es {medico.id_usuario}"
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Medico.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            # Crear slots mediante stored procedure
            creados = sp_agenda_create_range(
                id_usuario_medico,
                serializer.validated_data["fecha"],
                serializer.validated_data["hora_inicio"],
                serializer.validated_data["hora_fin"],
            )
            
        except DatabaseError as e:
            # Manejar errores específicos del stored procedure
            msg = str(e).lower()
            
            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "desactivado" in msg:
                return Response(
                    {
                        "detail": "El médico está desactivado.",
                        "hint": "Contacta al administrador para reactivar tu cuenta."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "documentación aprobada" in msg:
                return Response(
                    {
                        "detail": "No tienes toda la documentación aprobada.",
                        "hint": "Debes subir y validar todos los documentos requeridos."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "no está validado" in msg:
                return Response(
                    {
                        "detail": "Tu cuenta de médico no está validada.",
                        "hint": "Espera a que un administrador valide tu cuenta."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "fechas pasadas" in msg:
                return Response(
                    {"detail": "No se puede crear agenda en fechas pasadas."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "horarios deben estar" in msg:
                return Response(
                    {"detail": "Los horarios deben estar entre 06:00 y 22:00."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "hora fin" in msg:
                return Response(
                    {"detail": "La hora fin debe ser mayor que la hora inicio."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": "Agenda creada correctamente.",
                "slots_creados": creados,
                "fecha": serializer.validated_data["fecha"],
                "rango": f"{serializer.validated_data['hora_inicio']} - {serializer.validated_data['hora_fin']}"
            },
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, pk=None):
        """
        GET /api/agendas/:id_usuario_medico/
        
        Obtiene todos los slots de agenda de un médico (disponibles y ocupados).
        
        Permiso: Público (sin autenticación)
        
        Uso: Pacientes pueden ver la agenda completa para saber qué días
              el médico tiene horarios (aunque algunos estén ocupados)
        
        Args:
            pk: ID del usuario médico
        
        Response:
            200: Lista de slots de agenda
            404: Usuario no es médico
        """
        try:
            rows = sp_agenda_list_by_usuario(int(pk))
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Formatear respuesta
        data = [
            {
                "id_agenda": r["ID_Agenda"],
                "fecha": r["Fecha"],
                "hora": r["Hora"],
                "disponible": bool(r["Disponible"]),
            }
            for r in rows
        ]
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='disponible')
    def disponible(self, request, pk=None):
        """
        GET /api/agendas/:id_usuario_medico/disponible/
        
        Obtiene solo los slots DISPONIBLES de un médico.
        
        Permiso: Público (sin autenticación)
        
        Uso: Pacientes seleccionan un horario disponible para crear una cita
        
        Args:
            pk: ID del usuario médico
        
        Response:
            200: Lista de slots disponibles
            404: Usuario no es médico
        """
        try:
            rows = sp_agenda_list_disponible_by_usuario(int(pk))
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Formatear respuesta
        data = [
            {
                "id_agenda": r["ID_Agenda"],
                "fecha": r["Fecha"],
                "hora": r["Hora"],
            }
            for r in rows
        ]
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'], url_path='toggle')
    def toggle(self, request, pk=None):
        """
        PUT /api/agendas/toggle/:id_agenda/
        
        Activa o desactiva un slot de agenda.
        
        Permiso: Solo el médico dueño del slot
        
        Uso: Médico puede bloquear horarios (ej: vacaciones, ocupado)
        o reactivarlos cuando esté disponible nuevamente
        
        Args:
            pk: ID del slot de agenda
        
        Request Body:
            {
                "id_usuario_medico": 2,
                "disponible": false
            }
        
        Response:
            200: Estado actualizado
            403: No es el dueño del slot
            404: Usuario no es médico
        """
        serializer = AgendaToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        id_usuario_medico = serializer.validated_data["id_usuario_medico"]
        disponible = serializer.validated_data["disponible"]
        
        # VALIDACIÓN DE OWNERSHIP: Solo el médico dueño puede modificar
        if request.user.rol == 'Medico':
            # Obtener el ID_Medico del usuario autenticado
            from medicos.models import Medico
            try:
                medico = Medico.objects.get(id_usuario=request.user.id_usuario)
                
                # Verificar que el médico esté modificando su propia agenda
                if medico.id_usuario != id_usuario_medico:
                    return Response(
                        {
                            "detail": "Solo puedes modificar tu propia agenda.",
                            "hint": f"Tu ID de usuario médico es {medico.id_usuario}"
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Medico.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            # Actualizar disponibilidad mediante stored procedure
            afectadas = sp_agenda_toggle_slot(id_usuario_medico, int(pk), disponible)
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "no pertenece a este médico" in msg:
                return Response(
                    {
                        "detail": "Esta franja de agenda no te pertenece.",
                        "hint": "Solo puedes modificar tus propios slots de agenda."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": "Estado de disponibilidad actualizado correctamente.",
                "filas_afectadas": afectadas,
                "nuevo_estado": "disponible" if disponible else "no disponible"
            },
            status=status.HTTP_200_OK
        )


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - create: IsMedico + validación de ownership (solo su agenda)
#    - retrieve/disponible: AllowAny (lectura pública)
#    - toggle: IsAuthenticated + validación de ownership
#
# 2. VALIDACIÓN DE OWNERSHIP:
#    En create() y toggle():
#    - Obtener Medico del usuario autenticado
#    - Verificar que id_usuario_medico coincida
#    - Si no coincide → 403 Forbidden
#
# 3. LECTURA PÚBLICA:
#    - retrieve() y disponible() son públicos
#    - Pacientes necesitan ver horarios para crear citas
#    - No revelan información sensible del médico
#
# 4. STORED PROCEDURES:
#    - No se modifican
#    - Validaciones de negocio permanecen en el SP
#    - Permisos de acceso se validan ANTES en Django
#
# 5. FLUJO TÍPICO:
#    a) Médico crea agenda con create()
#    b) Paciente ve disponibilidad con disponible()
#    c) Paciente crea cita con ese slot
#    d) Médico puede desactivar slots con toggle()
#
# =============================================================================
