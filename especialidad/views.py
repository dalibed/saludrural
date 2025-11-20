"""
Views para el módulo de Especialidades

Gestiona el catálogo de especialidades médicas y su asignación a médicos.
Con PERMISOS implementados.

Lógica de permisos:
- Listar especialidades: Público (pacientes buscan por especialidad)
- Crear especialidad: Solo Admin
- Asignar especialidad: Solo Admin
- Listar especialidades de médico: Público
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import DatabaseError

from backend.permissions import IsAdministrador

from .serializers import (
    EspecialidadCreateSerializer,
    AsignarEspecialidadSerializer
)
from .services import (
    sp_especialidad_create,
    sp_especialidad_list,
    sp_medico_especialidad_asignar,
    sp_medico_especialidad_list
)


class EspecialidadViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Especialidades Médicas.
    
    Endpoints:
    - POST /api/especialidades/                        → Crear especialidad (admin)
    - GET  /api/especialidades/                        → Listar todas (público)
    - POST /api/especialidades/asignar/                → Asignar a médico (admin)
    - GET  /api/especialidades/medico/:id_usuario/     → Listar de médico (público)
    
    Permisos:
    - create/asignar: Solo Administradores
    - list/listar_por_medico: Público (pacientes buscan especialidades)
    """
    
    def get_permissions(self):
        """
        Define permisos según la acción.
        
        - create, asignar: Solo Admin
        - list, listar_por_medico: Público
        """
        if self.action in ['create', 'asignar']:
            return [IsAdministrador()]
        return [AllowAny()]
    
    # =========================================================================
    # ENDPOINTS PÚBLICOS (Búsqueda de especialidades)
    # =========================================================================
    
    def list(self, request):
        """
        GET /api/especialidades/
        
        Lista todas las especialidades disponibles.
        
        Permiso: Público
        
        Uso: Pacientes buscan médicos por especialidad
        
        Response:
            200: Lista de especialidades
            [
                {
                    "ID_Especialidad": 1,
                    "Nombre": "Cardiología",
                    "Descripcion": "Especialidad del corazón"
                }
            ]
        """
        rows = sp_especialidad_list()
        return Response(rows, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='medico')
    def listar_por_medico(self, request, pk=None):
        """
        GET /api/especialidades/medico/:id_usuario_medico/
        
        Lista las especialidades de un médico específico.
        
        Permiso: Público
        
        Args:
            pk: ID del usuario médico
        
        Response:
            200: Lista de especialidades del médico
            404: Médico no encontrado
        """
        try:
            rows = sp_medico_especialidad_list(int(pk))
            
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
        
        return Response(rows, status=status.HTTP_200_OK)
    
    # =========================================================================
    # ENDPOINTS DE ADMINISTRACIÓN
    # =========================================================================
    
    def create(self, request):
        """
        POST /api/especialidades/
        
        Crea una nueva especialidad en el catálogo.
        
        Permiso: Solo Administradores
        
        Request Body:
            {
                "nombre": "Cardiología",
                "descripcion": "Especialidad del corazón y sistema circulatorio"
            }
        
        Response:
            201: Especialidad creada
            400: Ya existe o datos inválidos
            403: No es administrador
        """
        serializer = EspecialidadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            new_id = sp_especialidad_create(data["nombre"], data["descripcion"])
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "ya existe" in msg:
                return Response(
                    {
                        "detail": "La especialidad ya existe.",
                        "hint": "Verifica el nombre de la especialidad."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": "Especialidad creada correctamente.",
                "id_especialidad": new_id
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'], url_path='asignar')
    def asignar(self, request):
        """
        POST /api/especialidades/asignar/
        
        Asigna una especialidad a un médico.
        
        Permiso: Solo Administradores
        
        Request Body:
            {
                "id_usuario_medico": 2,
                "id_especialidad": 1
            }
        
        Response:
            200: Especialidad asignada
            404: Médico o especialidad no encontrada
            403: No es administrador
        """
        serializer = AsignarEspecialidadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            affected = sp_medico_especialidad_asignar(
                data["id_usuario_medico"],
                data["id_especialidad"]
            )
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "médico no existe" in msg:
                return Response(
                    {"detail": "El médico no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "especialidad no existe" in msg:
                return Response(
                    {"detail": "La especialidad no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "detail": "Especialidad asignada correctamente.",
                "filas_afectadas": affected
            },
            status=status.HTTP_200_OK
        )


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - list: AllowAny (público para búsqueda)
#    - listar_por_medico: AllowAny (público)
#    - create: IsAdministrador
#    - asignar: IsAdministrador
#
# 2. USO TÍPICO:
#    - Paciente busca médicos por especialidad
#    - Admin crea especialidades nuevas
#    - Admin asigna especialidades a médicos
#
# 3. FLUJO:
#    a) Admin crea especialidad (POST /especialidades/)
#    b) Admin asigna a médico (POST /especialidades/asignar/)
#    c) Paciente busca médicos con esa especialidad
#
# =============================================================================