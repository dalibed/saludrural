"""
Views para el módulo de Citas

Este módulo maneja las citas médicas entre pacientes y médicos.
Ahora con PERMISOS implementados para proteger la información médica.

Lógica de permisos:
- Crear cita (create): Solo Pacientes, solo para sí mismos
- Cancelar cita (cancelar): Paciente/Médico involucrados o Admin
- Completar cita (completar): Solo el médico asignado
- Ver citas de paciente: Solo el paciente mismo o Admin
- Ver citas de médico: Solo el médico mismo o Admin
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import DatabaseError

# Importar permisos personalizados
from backend.permissions import IsPaciente, IsMedico, IsAdministrador

from .serializers import (
    CrearCitaSerializer,
    CancelarCitaSerializer,
    CitaSerializer
)
from .services import (
    sp_cita_create,
    sp_cita_cancelar,
    sp_cita_list_paciente,
    sp_cita_list_medico,
    sp_cita_completar,
    sp_cita_aceptar
)


class CitaViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Citas Médicas.
    
    Endpoints:
    - POST   /api/citas/                       → Crear cita (solo paciente)
    - PUT    /api/citas/cancelar/:id/          → Cancelar cita (involucrados)
    - PUT    /api/citas/completar/:id/         → Completar cita (solo médico asignado)
    - GET    /api/citas/paciente/:id_usuario/  → Ver citas de paciente
    - GET    /api/citas/medico/:id_usuario/    → Ver citas de médico
    
    Permisos implementados:
    - create: Solo Pacientes + validación ownership
    - cancelar: Autenticado + validación de participación en la cita
    - completar: Solo Médicos + validación de asignación
    - citas_paciente: Autenticado + validación ownership
    - citas_medico: Autenticado + validación ownership
    """
    
    def get_permissions(self):
        """
        Define los permisos según la acción.
        
        Lógica:
        - create: Solo pacientes
        - cancelar/completar: Autenticado (validación en método)
        - citas_paciente/citas_medico: Autenticado (validación en método)
        
        Returns:
            list: Lista de instancias de permisos
        """
        if self.action == 'create':
            # Solo pacientes pueden crear citas
            return [IsPaciente()]
        
        else:
            # Resto de acciones: autenticado + validación en método
            return [IsAuthenticated()]
    
    # =========================================================================
    # ENDPOINTS CRUD
    # =========================================================================
    
    def create(self, request):
        """
        POST /api/citas/
        
        Crea una nueva cita médica.
        
        Permiso: Solo Pacientes
        
        Validaciones adicionales:
        - Paciente solo puede crear citas para sí mismo
        - El horario debe estar disponible
        - No puede crear citas en el pasado
        - No puede tener múltiples citas a la misma hora
        
        Request Body:
            {
                "id_usuario_paciente": 1,
                "id_usuario_medico": 2,
                "id_agenda": 5,
                "motivo_consulta": "Dolor de cabeza persistente"
            }
        
        Response:
            201: Cita creada
            400: Datos inválidos o horario no disponible
            403: Paciente/Médico desactivado o no validado
            404: Usuario no registrado
        """
        serializer = CrearCitaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        id_usuario_paciente = data["id_usuario_paciente"]
        
        # VALIDACIÓN DE OWNERSHIP: Paciente solo crea citas para sí mismo
        from pacientes.models import Paciente
        try:
            paciente = Paciente.objects.get(id_usuario=request.user.id_usuario)
            
            # Verificar que el paciente esté creando su propia cita
            if paciente.id_usuario != id_usuario_paciente:
                return Response(
                    {
                        "detail": "Solo puedes crear citas para ti mismo.",
                        "hint": f"Tu ID de usuario es {paciente.id_usuario}"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except Paciente.DoesNotExist:
            return Response(
                {"detail": "No estás registrado como paciente."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Crear cita mediante stored procedure
            id_cita = sp_cita_create(
                id_usuario_paciente,
                data["id_usuario_medico"],
                data["id_agenda"],
                data["motivo_consulta"]
            )
            
        except DatabaseError as e:
            # Manejar errores específicos del stored procedure
            msg = str(e).lower()
            
            if "no está registrado como paciente" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "paciente está desactivado" in msg:
                return Response(
                    {
                        "detail": "Tu cuenta de paciente está desactivada.",
                        "hint": "Contacta al administrador para reactivarla."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El médico seleccionado no está registrado."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "médico está desactivado" in msg:
                return Response(
                    {"detail": "El médico seleccionado está desactivado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "médico no está aprobado" in msg:
                return Response(
                    {
                        "detail": "El médico no está aprobado para recibir citas.",
                        "hint": "Selecciona otro médico con perfil validado."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "ya no está disponible" in msg:
                return Response(
                    {
                        "detail": "Este horario ya no está disponible.",
                        "hint": "Por favor selecciona otro horario."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "no se pueden crear citas en el pasado" in msg:
                return Response(
                    {"detail": "No se pueden crear citas en el pasado."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "ya tiene una cita programada" in msg:
                return Response(
                    {
                        "detail": "Ya tienes una cita programada a esa hora.",
                        "hint": "No puedes tener múltiples citas al mismo tiempo."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "no pertenece a este médico" in msg:
                return Response(
                    {
                        "detail": "La franja horaria no pertenece a este médico.",
                        "hint": "Verifica que el ID de agenda corresponda al médico."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": "Cita creada correctamente.",
                "id_cita": id_cita
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['put'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """
        PUT /api/citas/cancelar/:id_cita/
        
        Cancela una cita existente.
        
        Permiso: Paciente involucrado, Médico involucrado o Administrador
        
        Validaciones:
        - Solo puede cancelar si es el paciente, el médico o admin
        - No se puede cancelar una cita ya completada
        - No se puede cancelar una cita ya cancelada
        
        Args:
            pk: ID de la cita a cancelar
        
        Request Body:
            {
                "id_usuario": 1,
                "motivo_cancelacion": "No puedo asistir" (opcional)
            }
        
        Response:
            200: Cita cancelada
            400: Cita ya cancelada o completada
            403: No tiene permisos para cancelar
            404: Cita no existe
        """
        serializer = CancelarCitaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        id_usuario = data["id_usuario"]
        
        # VALIDACIÓN DE OWNERSHIP: Solo el involucrado o admin pueden cancelar
        if request.user.rol != 'Administrador':
            # Verificar que el usuario autenticado sea quien quiere cancelar
            if request.user.id_usuario != id_usuario:
                return Response(
                    {
                        "detail": "No puedes cancelar citas en nombre de otros usuarios.",
                        "hint": "Solo puedes cancelar tus propias citas."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            # Cancelar cita mediante stored procedure
            # El SP valida que id_usuario sea paciente o médico de la cita
            afectadas = sp_cita_cancelar(
                int(pk),
                id_usuario,
                data.get("motivo_cancelacion", "Sin motivo especificado")
            )
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "cita no existe" in msg:
                return Response(
                    {"detail": "La cita no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "ya está cancelada" in msg:
                return Response(
                    {"detail": "La cita ya está cancelada."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "no se puede cancelar una cita completada" in msg:
                return Response(
                    {"detail": "No se puede cancelar una cita completada."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "no tiene permisos" in msg:
                return Response(
                    {
                        "detail": "No tienes permisos para cancelar esta cita.",
                        "hint": "Solo el paciente o médico involucrado pueden cancelar."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": "Cita cancelada correctamente.",
                "filas_afectadas": afectadas
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['put'], url_path='aceptar')
    def aceptar(self, request, pk=None):
        """
        PUT /api/citas/aceptar/:id_cita/
        
        Acepta una cita pendiente, cambiándola a estado "Programada".
        
        Permiso: Solo el médico asignado a la cita
        
        Validaciones:
        - Solo el médico asignado puede aceptar
        - La cita debe estar en estado "Pendiente"
        - No se puede aceptar una cita cancelada o completada
        
        Args:
            pk: ID de la cita a aceptar
        
        Request Body:
            {
                "id_usuario_medico": 2
            }
        
        Response:
            200: Cita aceptada
            400: Cita no está en estado Pendiente o ya fue procesada
            403: No es el médico asignado
            404: Cita no existe
        """
        id_usuario_medico = request.data.get("id_usuario_medico")
        
        if not id_usuario_medico:
            return Response(
                {"detail": "Debe enviar id_usuario_medico."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # VALIDACIÓN DE OWNERSHIP: Solo el médico autenticado puede aceptar
        if request.user.rol == 'Medico':
            from medicos.models import Medico
            try:
                medico = Medico.objects.get(id_usuario=request.user.id_usuario)
                
                # id_usuario es un IntegerField, no una ForeignKey, así que es directamente el ID
                id_usuario_medico_actual = medico.id_usuario
                
                # Verificar que el médico esté aceptando su propia cita
                if int(id_usuario_medico_actual) != int(id_usuario_medico):
                    return Response(
                        {
                            "detail": "Solo puedes aceptar tus propias citas.",
                            "hint": f"Tu ID de usuario médico es {id_usuario_medico_actual}, pero estás intentando usar {id_usuario_medico}"
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Medico.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            # Aceptar cita mediante stored procedure
            # El SP valida que el médico sea el asignado a la cita y que esté en estado Pendiente
            mensaje = sp_cita_aceptar(
                int(id_usuario_medico),
                int(pk)
            )
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "médico está desactivado" in msg:
                return Response(
                    {"detail": "El médico está desactivado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "médico no está aprobado" in msg:
                return Response(
                    {"detail": "El médico no está aprobado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "cita no existe" in msg:
                return Response(
                    {"detail": "La cita no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "solo el médico asignado" in msg:
                return Response(
                    {
                        "detail": "Solo el médico asignado puede aceptar la cita.",
                        "hint": "Esta cita no te pertenece."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "no está en estado pendiente" in msg or "ya está programada" in msg:
                return Response(
                    {"detail": "La cita no está en estado Pendiente o ya fue procesada."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "no se puede aceptar una cita cancelada" in msg or "no se puede aceptar una cita completada" in msg:
                return Response(
                    {"detail": "No se puede aceptar una cita que ya fue cancelada o completada."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {"detail": mensaje},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['put'], url_path='completar')
    def completar(self, request, pk=None):
        """
        PUT /api/citas/completar/:id_cita/
        
        Marca una cita como completada (realizada).
        
        Permiso: Solo el médico asignado a la cita
        
        Validaciones:
        - Solo el médico asignado puede completar
        - No se puede completar una cita cancelada
        - No se puede completar una cita ya completada
        
        Args:
            pk: ID de la cita a completar
        
        Request Body:
            {
                "id_usuario_medico": 2
            }
        
        Response:
            200: Cita completada
            400: Cita ya completada o cancelada
            403: No es el médico asignado
            404: Cita no existe
        """
        id_usuario_medico = request.data.get("id_usuario_medico")
        
        if not id_usuario_medico:
            return Response(
                {"detail": "Debe enviar id_usuario_medico."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # VALIDACIÓN DE OWNERSHIP: Solo el médico autenticado puede completar
        if request.user.rol == 'Medico':
            from medicos.models import Medico
            try:
                medico = Medico.objects.get(id_usuario=request.user.id_usuario)
                
                # id_usuario es un IntegerField, no una ForeignKey, así que es directamente el ID
                id_usuario_medico_actual = medico.id_usuario
                
                # Verificar que el médico esté completando su propia cita
                if int(id_usuario_medico_actual) != int(id_usuario_medico):
                    return Response(
                        {
                            "detail": "Solo puedes completar tus propias citas.",
                            "hint": f"Tu ID de usuario médico es {id_usuario_medico_actual}, pero estás intentando usar {id_usuario_medico}"
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Medico.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            # Completar cita mediante stored procedure
            # El SP valida que el médico sea el asignado a la cita
            mensaje = sp_cita_completar(
                int(id_usuario_medico),
                int(pk)
            )
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "médico está desactivado" in msg:
                return Response(
                    {"detail": "El médico está desactivado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "médico no está aprobado" in msg:
                return Response(
                    {"detail": "El médico no está aprobado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "cita no existe" in msg:
                return Response(
                    {"detail": "La cita no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "solo el médico asignado" in msg:
                return Response(
                    {
                        "detail": "Solo el médico asignado puede completar la cita.",
                        "hint": "Esta cita no te pertenece."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "ya está completada" in msg:
                return Response(
                    {"detail": "La cita ya está completada."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "no se puede completar una cita cancelada" in msg:
                return Response(
                    {"detail": "No se puede completar una cita cancelada."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {"detail": mensaje},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], url_path='paciente')
    def citas_paciente(self, request, pk=None):
        """
        GET /api/citas/paciente/:id_usuario/
        
        Obtiene todas las citas de un paciente.
        
        Permiso: Solo el paciente mismo o Administrador
        
        Args:
            pk: ID del usuario paciente
        
        Response:
            200: Lista de citas del paciente
            403: No tiene permiso para ver estas citas
            404: Usuario no es paciente
        """
        # VALIDACIÓN DE OWNERSHIP: Paciente solo ve sus citas
        if request.user.rol != 'Administrador':
            if request.user.id_usuario != int(pk):
                return Response(
                    {
                        "detail": "No tienes permiso para ver las citas de otros pacientes.",
                        "hint": "Solo puedes ver tus propias citas."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            rows = sp_cita_list_paciente(int(pk))
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no está registrado como paciente" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(rows, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='medico')
    def citas_medico(self, request, pk=None):
        """
        GET /api/citas/medico/:id_usuario/
        
        Obtiene todas las citas de un médico.
        
        Permiso: Solo el médico mismo o Administrador
        
        Args:
            pk: ID del usuario médico
        
        Response:
            200: Lista de citas del médico
            403: No tiene permiso para ver estas citas
            404: Usuario no es médico
        """
        # VALIDACIÓN DE OWNERSHIP: Médico solo ve sus citas
        if request.user.rol != 'Administrador':
            if request.user.id_usuario != int(pk):
                return Response(
                    {
                        "detail": "No tienes permiso para ver las citas de otros médicos.",
                        "hint": "Solo puedes ver tus propias citas."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            rows = sp_cita_list_medico(int(pk))
            
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
        
        return Response(rows, status=status.HTTP_200_OK)


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - create: IsPaciente + validación ownership (solo sus citas)
#    - cancelar: IsAuthenticated + validación de involucrado
#    - completar: IsAuthenticated + validación de médico asignado
#    - citas_paciente: IsAuthenticated + validación ownership
#    - citas_medico: IsAuthenticated + validación ownership
#
# 2. VALIDACIÓN DE OWNERSHIP:
#    - En create(): Paciente solo crea para sí mismo
#    - En cancelar(): Usuario cancela solo sus citas
#    - En completar(): Médico completa solo citas asignadas a él
#    - En citas_paciente(): Paciente ve solo sus citas
#    - En citas_medico(): Médico ve solo sus citas
#    - Admin puede todo
#
# 3. FLUJO TÍPICO:
#    a) Paciente crea cita con create()
#    b) Médico ve sus citas con citas_medico()
#    c) Médico completa cita con completar()
#    d) Si necesita, paciente/médico cancela con cancelar()
#
# 4. STORED PROCEDURES:
#    - Los SPs tienen validaciones de negocio
#    - Django valida permisos ANTES de llamar al SP
#    - Si el SP lanza error, Django lo interpreta y retorna mensaje claro
#
# 5. SEGURIDAD:
#    - Información médica protegida
#    - Solo involucrados ven sus citas
#    - No se pueden modificar citas ajenas
#    - Mensajes de error no revelan info sensible
#
# =============================================================================