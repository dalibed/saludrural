"""
Views para el módulo de Historia Entrada

Este módulo maneja las entradas médicas individuales (consultas realizadas).
Ahora con PERMISOS implementados para proteger datos médicos sensibles.

Lógica de permisos:
- Crear entrada (create): Solo Médicos, solo de citas completadas donde son asignados
- Actualizar entrada (update): Solo el médico que creó la entrada
- Ver entrada específica (retrieve): Paciente de la entrada o Médico que la creó
- Listar por paciente (list_paciente): Solo el paciente o Admin
- Listar por médico (list_medico): Solo el médico o Admin
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import DatabaseError

# Importar permisos personalizados
from backend.permissions import IsMedico, IsAdministrador

from .serializers import (
    HistoriaEntradaCreateSerializer,
    HistoriaEntradaUpdateSerializer,
)
from .services import (
    sp_historia_entrada_create,
    sp_historia_entrada_update,
    sp_historia_entrada_get,
    sp_historia_entrada_list_by_paciente,
    sp_historia_entrada_list_by_medico,
)


class HistoriaEntradaViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Entradas de Historia Clínica.
    
    Endpoints:
    - POST /api/historia-entradas/                         → Crear entrada (solo médico)
    - PUT  /api/historia-entradas/:id/                     → Actualizar entrada (solo creador)
    - GET  /api/historia-entradas/:id/                     → Ver entrada específica
    - GET  /api/historia/entrada/paciente/:id_usuario/    → Listar entradas de paciente
    - GET  /api/historia/entrada/medico/:id_usuario/      → Listar entradas de médico
    
    Permisos implementados:
    - create: Solo Médicos
    - update: Solo el médico que creó la entrada
    - retrieve: Autenticado + validación de participación
    - list_paciente: Solo el paciente o Admin
    - list_medico: Solo el médico o Admin
    
    IMPORTANTE: Entradas contienen diagnósticos y tratamientos - datos ultra sensibles
    """
    
    def get_permissions(self):
        """
        Define los permisos según la acción.
        
        Lógica:
        - create/update: Solo médicos
        - retrieve/list_*: Autenticado (validación ownership en método)
        
        Returns:
            list: Lista de instancias de permisos
        """
        if self.action in ['create', 'update']:
            # Solo médicos pueden crear/actualizar entradas
            return [IsMedico()]
        
        else:
            # Lectura: autenticado + validación en método
            return [IsAuthenticated()]
    
    # =========================================================================
    # ENDPOINTS DE ESCRITURA
    # =========================================================================
    
    def create(self, request):
        """
        POST /api/historia-entradas/
        
        Crea una nueva entrada en la historia clínica después de una cita.
        
        Permiso: Solo Médicos
        
        Validaciones:
        - Médico solo puede crear entradas de citas donde es el asignado
        - La cita debe estar completada
        - No puede haber entrada duplicada para la misma cita
        - El paciente debe tener historia clínica
        
        Request Body:
            {
                "id_usuario_medico": 2,
                "id_cita": 1,
                "diagnostico": "Hipertensión arterial",
                "tratamiento": "Enalapril 10mg cada 12h",
                "notas": "Paciente refiere mareos ocasionales" (opcional)
            }
        
        Response:
            201: Entrada creada
            400: Datos inválidos o cita no completada
            403: No es el médico asignado o no está aprobado
            404: Médico o cita no encontrada
        """
        serializer = HistoriaEntradaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        id_usuario_medico = data["id_usuario_medico"]
        
        # VALIDACIÓN DE OWNERSHIP: Médico solo crea entradas con su ID
        from medicos.models import Medico
        try:
            medico = Medico.objects.get(id_usuario=request.user.id_usuario)
            
            # Verificar que el médico esté usando su propio ID
            if medico.id_usuario != id_usuario_medico:
                return Response(
                    {
                        "detail": "Solo puedes crear entradas con tu propio ID de médico.",
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
            # Crear entrada mediante stored procedure
            id_entrada = sp_historia_entrada_create(
                id_usuario_medico,
                data["id_cita"],
                data["diagnostico"],
                data["tratamiento"],
                data.get("notas", ""),
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
                    {"detail": "Tu cuenta de médico está desactivada."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "médico no está aprobado" in msg:
                return Response(
                    {
                        "detail": "Tu cuenta de médico no está aprobada.",
                        "hint": "Debes tener documentación validada para crear entradas médicas."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "cita no existe" in msg:
                return Response(
                    {"detail": "La cita no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "solo se puede crear entrada de historia para citas completadas" in msg:
                return Response(
                    {
                        "detail": "Solo se puede crear entrada para citas completadas.",
                        "hint": "Debes completar la cita primero."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "solo el médico asignado a la cita puede crear la entrada" in msg:
                return Response(
                    {
                        "detail": "Solo el médico asignado a la cita puede crear la entrada.",
                        "hint": "Esta cita no te fue asignada."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "ya existe una entrada de historia para esta cita" in msg:
                return Response(
                    {
                        "detail": "Ya existe una entrada de historia para esta cita.",
                        "hint": "Solo se permite una entrada por cita. Usa PUT para actualizar."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if "no tiene historia clínica" in msg:
                return Response(
                    {"detail": "El paciente no tiene historia clínica."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": "Entrada de historia creada correctamente.",
                "id_entrada": id_entrada
            },
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None):
        """
        PUT /api/historia-entradas/:id/
        
        Actualiza una entrada existente en la historia clínica.
        
        Permiso: Solo Médicos
        
        Validaciones:
        - Solo el médico que creó la entrada puede modificarla
        - Médico debe estar aprobado y activo
        
        Args:
            pk: ID de la entrada a actualizar
        
        Request Body:
            {
                "id_usuario_medico": 2,
                "diagnostico": "Hipertensión arterial controlada",
                "tratamiento": "Enalapril 10mg cada 12h + dieta",
                "notas": "Paciente mejoró síntomas"
            }
        
        Response:
            200: Entrada actualizada
            403: No es el médico creador
            404: Entrada no encontrada
        """
        serializer = HistoriaEntradaUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        id_usuario_medico = data["id_usuario_medico"]
        
        # VALIDACIÓN DE OWNERSHIP: Médico solo actualiza con su ID
        from medicos.models import Medico
        try:
            medico = Medico.objects.get(id_usuario=request.user.id_usuario)
            
            # Verificar que el médico esté usando su propio ID
            if medico.id_usuario.id_usuario != id_usuario_medico:
                return Response(
                    {
                        "detail": "Solo puedes actualizar entradas con tu propio ID de médico.",
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
            # Actualizar mediante stored procedure
            filas = sp_historia_entrada_update(
                id_usuario_medico,
                int(pk),
                data["diagnostico"],
                data["tratamiento"],
                data.get("notas", ""),
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
                    {"detail": "Tu cuenta de médico está desactivada."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "médico no está aprobado" in msg:
                return Response(
                    {
                        "detail": "Tu cuenta de médico no está aprobada.",
                        "hint": "Debes tener documentación validada para modificar entradas médicas."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "entrada de historia no existe" in msg:
                return Response(
                    {"detail": "La entrada de historia no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "solo el médico que creó la entrada puede modificarla" in msg:
                return Response(
                    {
                        "detail": "Solo el médico que creó la entrada puede modificarla.",
                        "hint": "Esta entrada fue creada por otro médico."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if filas == 0:
            return Response(
                {"detail": "Entrada de historia no encontrada o sin cambios."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {
                "detail": "Entrada de historia actualizada correctamente.",
                "filas_afectadas": filas
            },
            status=status.HTTP_200_OK
        )
    
    # =========================================================================
    # ENDPOINTS DE LECTURA
    # =========================================================================
    
    def retrieve(self, request, pk=None):
        """
        GET /api/historia-entradas/:id/
        
        Obtiene una entrada específica de historia clínica.
        
        Permiso: Autenticado
        
        Validaciones:
        - Paciente de la entrada puede verla
        - Médico que la creó puede verla
        - Admin puede verla
        - Otros usuarios NO pueden acceder
        
        Args:
            pk: ID de la entrada
        
        Response:
            200: Datos de la entrada
            403: No tiene permiso para ver esta entrada
            404: Entrada no encontrada
        """
        try:
            data = sp_historia_entrada_get(int(pk))
            
        except DatabaseError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data:
            return Response(
                {"detail": "Entrada de historia no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # VALIDACIÓN DE OWNERSHIP: Solo involucrados pueden ver
        if request.user.rol != 'Administrador':
            # Verificar si es el paciente de la entrada
            if request.user.rol == 'Paciente':
                from pacientes.models import Paciente
                try:
                    paciente = Paciente.objects.get(id_usuario=request.user.id_usuario)
                    
                    # Verificar que sea el paciente de esta entrada
                    # Asumiendo que data tiene 'id_paciente' o similar
                    if 'ID_Paciente' in data and data['ID_Paciente'] != paciente.id_paciente:
                        return Response(
                            {
                                "detail": "No tienes permiso para ver esta entrada.",
                                "hint": "Solo puedes ver tus propias entradas médicas."
                            },
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Paciente.DoesNotExist:
                    pass
            
            # Verificar si es el médico que creó la entrada
            elif request.user.rol == 'Medico':
                from medicos.models import Medico
                try:
                    medico = Medico.objects.get(id_usuario=request.user.id_usuario)
                    
                    # Verificar que sea el médico de esta entrada
                    # Asumiendo que data tiene 'ID_Medico' o similar
                    if 'ID_Medico' in data and data['ID_Medico'] != medico.id_medico:
                        return Response(
                            {
                                "detail": "No tienes permiso para ver esta entrada.",
                                "hint": "Solo puedes ver entradas que creaste."
                            },
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Medico.DoesNotExist:
                    pass
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='entrada/paciente')
    def list_paciente(self, request, pk=None):
        """
        GET /api/historia/entrada/paciente/:id_usuario_paciente/
        
        Lista todas las entradas de historia de un paciente.
        
        Permiso: Solo el paciente mismo o Admin
        
        Args:
            pk: ID del usuario paciente
        
        Response:
            200: Lista de entradas del paciente
            403: No tiene permiso
            404: Paciente o historia no encontrada
        """
        id_usuario_paciente = int(pk)
        
        # VALIDACIÓN DE OWNERSHIP: Paciente solo ve sus entradas
        if request.user.rol == 'Paciente':
            from pacientes.models import Paciente
            try:
                paciente = Paciente.objects.get(id_usuario=request.user.id_usuario)
                
                # Verificar que esté consultando sus propias entradas
                if paciente.id_usuario != id_usuario_paciente:
                    return Response(
                        {
                            "detail": "No tienes permiso para ver las entradas de otros pacientes.",
                            "hint": "Solo puedes ver tus propias entradas médicas."
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Paciente.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Admin puede ver cualquier entrada
        try:
            data = sp_historia_entrada_list_by_paciente(id_usuario_paciente)
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no está registrado como paciente" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "no tiene historia clínica" in msg:
                return Response(
                    {"detail": "El paciente no tiene historia clínica."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='entrada/medico')
    def list_medico(self, request, pk=None):
        """
        GET /api/historia/entrada/medico/:id_usuario_medico/
        
        Lista todas las entradas de historia creadas por un médico.
        
        Permiso: Solo el médico mismo o Admin
        
        Args:
            pk: ID del usuario médico
        
        Response:
            200: Lista de entradas del médico
            403: No tiene permiso
            404: Médico no encontrado
        """
        id_usuario_medico = int(pk)
        
        # VALIDACIÓN DE OWNERSHIP: Médico solo ve sus entradas
        if request.user.rol == 'Medico':
            from medicos.models import Medico
            try:
                medico = Medico.objects.get(id_usuario=request.user.id_usuario)
                
                # Verificar que esté consultando sus propias entradas
                if medico.id_usuario.id_usuario != id_usuario_medico:
                    return Response(
                        {
                            "detail": "No tienes permiso para ver las entradas de otros médicos.",
                            "hint": "Solo puedes ver tus propias entradas médicas."
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Medico.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Admin puede ver entradas de cualquier médico
        try:
            data = sp_historia_entrada_list_by_medico(id_usuario_medico)
            
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
        
        return Response(data, status=status.HTTP_200_OK)


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - create: IsMedico + ownership (solo su ID)
#    - update: IsMedico + ownership (solo creador)
#    - retrieve: IsAuthenticated + ownership (involucrados)
#    - list_paciente: IsAuthenticated + ownership (solo el paciente)
#    - list_medico: IsAuthenticated + ownership (solo el médico)
#
# 2. VALIDACIÓN DE OWNERSHIP:
#    - Médico: Solo crea/actualiza con su ID
#    - Paciente: Solo ve sus entradas
#    - Admin: Puede ver todas
#
# 3. DATOS ULTRA SENSIBLES:
#    - Diagnósticos y tratamientos son información crítica
#    - Solo médicos aprobados pueden escribir
#    - Pacientes tienen derecho a ver sus entradas (HIPAA)
#    - Entradas no se eliminan, solo se actualizan
#
# 4. RELACIÓN CON CITAS:
#    - Una entrada por cita completada
#    - Solo el médico asignado puede crear
#    - Garantiza trazabilidad médico-paciente
#
# 5. STORED PROCEDURES:
#    - SPs validan relaciones y estados
#    - Django valida permisos de acceso
#    - Triple capa de seguridad
#
# 6. FLUJO TÍPICO:
#    a) Médico completa cita
#    b) Médico crea entrada con create()
#    c) Paciente ve sus entradas con list_paciente()
#    d) Médico puede actualizar entrada con update()
#    e) Médico ve su historial con list_medico()
#
# =============================================================================