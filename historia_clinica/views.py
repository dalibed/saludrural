"""
Views para el módulo de Historia Clínica

Este módulo maneja el registro médico base de cada paciente.
Ahora con PERMISOS implementados para proteger datos médicos sensibles.

Lógica de permisos:
- Ver historia (historia_paciente): Paciente ve solo la suya, Médico puede ver, Admin ve todas
- Actualizar antecedentes: Solo Médicos
- Ver historia completa: Solo Médicos con relación con el paciente
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import DatabaseError

# Importar permisos personalizados
from backend.permissions import IsMedico, IsAdministrador

from .serializers import AntecedentesUpdateSerializer
from .services import (
    sp_historia_clinica_get_by_paciente,
    sp_historia_clinica_update_antecedentes,
    sp_historia_completa_by_paciente,
)


class HistoriaClinicaViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Historia Clínica.
    
    Endpoints:
    - GET  /api/historia/paciente/:id_usuario_paciente/         → Ver historia básica
    - PUT  /api/historia/antecedentes/:id_medico/:id_paciente/  → Actualizar antecedentes
    - GET  /api/historia/completa/:id_medico/:id_paciente/      → Ver historia completa
    
    Permisos implementados:
    - historia_paciente: Paciente ve solo la suya, Médico/Admin pueden ver
    - actualizar_antecedentes: Solo Médicos
    - historia_completa: Solo Médicos
    
    IMPORTANTE: Datos médicos sensibles - validación estricta de ownership
    """
    
    def get_permissions(self):
        """
        Define los permisos según la acción.
        
        Lógica:
        - historia_paciente: Autenticado (validación ownership en método)
        - actualizar_antecedentes: Solo médicos
        - historia_completa: Solo médicos
        
        Returns:
            list: Lista de instancias de permisos
        """
        if self.action in ['actualizar_antecedentes', 'historia_completa']:
            # Solo médicos pueden actualizar o ver historia completa
            return [IsMedico()]
        
        else:
            # historia_paciente: Autenticado + validación en método
            return [IsAuthenticated()]
    
    # =========================================================================
    # ENDPOINTS DE LECTURA
    # =========================================================================
    
    @action(detail=True, methods=['get'], url_path='paciente')
    def historia_paciente(self, request, pk=None):
        """
        GET /api/historia/paciente/:id_usuario_paciente/
        
        Obtiene la historia clínica básica de un paciente.
        
        Permiso: 
        - Paciente puede ver solo su propia historia
        - Médico puede ver historia de cualquier paciente
        - Admin puede ver cualquier historia
        
        Args:
            pk: ID del usuario paciente
        
        Response:
            200: Datos de la historia clínica
            403: No tiene permiso para ver esta historia
            404: Paciente o historia no encontrada
        """
        id_usuario_paciente = int(pk)
        
        # VALIDACIÓN DE OWNERSHIP: Paciente solo ve su propia historia
        if request.user.rol == 'Paciente':
            from pacientes.models import Paciente
            try:
                paciente = Paciente.objects.get(id_usuario=request.user.id_usuario)
                
                # Verificar que el paciente esté viendo su propia historia
                if paciente.id_usuario != id_usuario_paciente:
                    return Response(
                        {
                            "detail": "No tienes permiso para ver la historia clínica de otros pacientes.",
                            "hint": "Solo puedes ver tu propia historia clínica."
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Paciente.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Médico y Admin pueden ver cualquier historia
        try:
            data = sp_historia_clinica_get_by_paciente(id_usuario_paciente)
            
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
        
        if not data:
            return Response(
                {"detail": "Historia clínica no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(data, status=status.HTTP_200_OK)
    
    # =========================================================================
    # ENDPOINTS DE ESCRITURA
    # =========================================================================
    
    @action(detail=False, methods=['put'], url_path='antecedentes/(?P<id_medico>[^/.]+)/(?P<id_paciente>[^/.]+)')
    def actualizar_antecedentes(self, request, id_medico=None, id_paciente=None):
        """
        PUT /api/historia/antecedentes/:id_medico/:id_paciente/
        
        Actualiza los antecedentes médicos de un paciente.
        
        Permiso: Solo Médicos
        
        Validaciones:
        - Médico solo puede actualizar si es su propio ID
        - Médico debe estar aprobado y activo
        - Paciente debe existir y tener historia clínica
        
        Args:
            id_medico: ID del médico que actualiza
            id_paciente: ID del paciente cuya historia se actualiza
        
        Request Body:
            {
                "antecedentes": "Texto con antecedentes médicos del paciente"
            }
        
        Response:
            200: Antecedentes actualizados
            403: No es el médico correcto o no está aprobado
            404: Médico, paciente o historia no encontrada
        """
        # VALIDACIÓN DE OWNERSHIP: Médico solo actualiza con su propio ID
        from medicos.models import Medico
        try:
            medico = Medico.objects.get(id_usuario=request.user.id_usuario)
            
            # Verificar que el médico esté usando su propio ID
            if medico.id_usuario.id_usuario != int(id_medico):
                return Response(
                    {
                        "detail": "Solo puedes actualizar historias usando tu propio ID de médico.",
                        "hint": f"Tu ID de usuario médico es {medico.id_usuario.id_usuario}"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except Medico.DoesNotExist:
            return Response(
                {"detail": "No estás registrado como médico."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar datos de entrada
        serializer = AntecedentesUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        antecedentes = serializer.validated_data["antecedentes"]
        
        try:
            # Actualizar mediante stored procedure
            filas = sp_historia_clinica_update_antecedentes(
                int(id_medico),
                int(id_paciente),
                antecedentes
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
                        "hint": "Debes tener documentación validada para modificar historias clínicas."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "paciente no existe" in msg:
                return Response(
                    {"detail": "El paciente no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "historia clínica no existe" in msg:
                return Response(
                    {"detail": "La historia clínica no existe para este paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if filas == 0:
            return Response(
                {"detail": "No se actualizó ningún registro."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {
                "detail": "Antecedentes médicos actualizados correctamente.",
                "filas_afectadas": filas
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='completa/(?P<id_medico>[^/.]+)/(?P<id_paciente>[^/.]+)')
    def historia_completa(self, request, id_medico=None, id_paciente=None):
        """
        GET /api/historia/completa/:id_medico/:id_paciente/
        
        Obtiene la historia clínica completa de un paciente (con todas las entradas).
        
        Permiso: Solo Médicos
        
        Validaciones:
        - Médico solo puede consultar con su propio ID
        - Médico debe estar aprobado y activo
        - Retorna historia base + todas las entradas médicas
        
        Args:
            id_medico: ID del médico que consulta
            id_paciente: ID del paciente cuya historia se consulta
        
        Response:
            200: Historia completa con entradas
            403: No es el médico correcto o no está aprobado
            404: Médico, paciente o historia no encontrada
        """
        # VALIDACIÓN DE OWNERSHIP: Médico solo consulta con su propio ID
        from medicos.models import Medico
        try:
            medico = Medico.objects.get(id_usuario=request.user.id_usuario)
            
            # Verificar que el médico esté usando su propio ID
            if medico.id_usuario.id_usuario != int(id_medico):
                return Response(
                    {
                        "detail": "Solo puedes consultar historias usando tu propio ID de médico.",
                        "hint": f"Tu ID de usuario médico es {medico.id_usuario.id_usuario}"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except Medico.DoesNotExist:
            return Response(
                {"detail": "No estás registrado como médico."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Obtener historia completa mediante stored procedure
            data = sp_historia_completa_by_paciente(
                int(id_medico),
                int(id_paciente)
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
                        "hint": "Debes tener documentación validada para acceder a historias clínicas."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "paciente no existe" in msg:
                return Response(
                    {"detail": "El paciente no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data.get("historia"):
            return Response(
                {"detail": "Historia clínica no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(data, status=status.HTTP_200_OK)


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - historia_paciente: IsAuthenticated + ownership (paciente solo su historia)
#    - actualizar_antecedentes: IsMedico + ownership (solo su ID)
#    - historia_completa: IsMedico + ownership (solo su ID)
#
# 2. VALIDACIÓN DE OWNERSHIP:
#    - Paciente: Solo ve su propia historia
#    - Médico: Usa su propio ID para actualizar/ver
#    - Admin: Puede ver todas las historias (en historia_paciente)
#
# 3. DATOS SENSIBLES:
#    - Historia clínica contiene datos médicos privados
#    - Antecedentes son especialmente sensibles
#    - Solo médicos aprobados pueden escribir
#    - Pacientes tienen derecho a ver su historia (HIPAA compliance)
#
# 4. STORED PROCEDURES:
#    - Los SPs validan relaciones médico-paciente
#    - Django valida permisos de acceso ANTES del SP
#    - Doble capa de seguridad
#
# 5. FLUJO TÍPICO:
#    a) Paciente se registra → Se crea historia clínica automática
#    b) Paciente ve su historia con historia_paciente()
#    c) Médico actualiza antecedentes con actualizar_antecedentes()
#    d) Médico ve historia completa con historia_completa()
#
# =============================================================================