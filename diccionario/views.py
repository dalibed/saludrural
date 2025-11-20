"""
Views para el módulo de Diccionario Médico

Gestiona el glosario de términos médicos para educación del paciente.
Con PERMISOS implementados.

Lógica de permisos:
- Listar/buscar/ver términos: Público (educación para pacientes)
- Crear/actualizar/eliminar: Solo Admin
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import OperationalError, DatabaseError

from backend.permissions import IsAdministrador

from .serializers import (
    DiccionarioCreateSerializer,
    DiccionarioUpdateSerializer,
)

from .services import (
    sp_diccionario_create,
    sp_diccionario_update,
    sp_diccionario_delete,
    sp_diccionario_get,
    sp_diccionario_list,
    sp_diccionario_search,
)


class DiccionarioViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión del Diccionario Médico.
    
    Endpoints:
    - GET    /api/diccionario/                 → Listar todos (público)
    - GET    /api/diccionario/:id/             → Ver término (público)
    - GET    /api/diccionario/buscar/?q=texto  → Buscar (público)
    - POST   /api/diccionario/                 → Crear término (admin)
    - PUT    /api/diccionario/:id/             → Actualizar término (admin)
    - DELETE /api/diccionario/:id/             → Eliminar término (admin)
    
    Permisos:
    - list/retrieve/search: Público (educación pacientes)
    - create/update/destroy: Solo Administradores
    """
    
    def get_permissions(self):
        """
        Define permisos según la acción.
        
        - Lectura: Público (educación)
        - Escritura: Solo Admin
        """
        if self.action in ['list', 'retrieve', 'search']:
            return [AllowAny()]
        return [IsAdministrador()]
    
    # =========================================================================
    # ENDPOINTS PÚBLICOS (Educación del paciente)
    # =========================================================================
    
    def list(self, request):
        """
        GET /api/diccionario/
        
        Lista todos los términos médicos del diccionario.
        
        Permiso: Público
        
        Uso: Pacientes aprenden sobre términos médicos
        
        Response:
            200: Lista de términos
            [
                {
                    "ID_Diccionario": 1,
                    "Termino": "Hipertensión",
                    "Definicion": "Presión arterial elevada",
                    "Causas": "Obesidad, estrés...",
                    "Tratamientos": "Medicación, dieta..."
                }
            ]
        """
        data = sp_diccionario_list()
        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """
        GET /api/diccionario/:id/
        
        Obtiene un término específico del diccionario.
        
        Permiso: Público
        
        Args:
            pk: ID del término
        
        Response:
            200: Datos del término
            404: Término no encontrado
        """
        data = sp_diccionario_get(int(pk))
        
        if not data:
            return Response(
                {"detail": "Término no encontrado en el diccionario."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='buscar')
    def search(self, request):
        """
        GET /api/diccionario/buscar/?q=texto
        
        Busca términos médicos por texto.
        
        Permiso: Público
        
        Query Params:
            q: Texto a buscar (en término o definición)
        
        Response:
            200: Lista de términos que coinciden
        """
        busqueda = request.query_params.get("q", "")
        results = sp_diccionario_search(busqueda)
        return Response(results, status=status.HTTP_200_OK)
    
    # =========================================================================
    # ENDPOINTS DE ADMINISTRACIÓN
    # =========================================================================
    
    def create(self, request):
        """
        POST /api/diccionario/
        
        Crea un nuevo término en el diccionario médico.
        
        Permiso: Solo Administradores
        
        Request Body:
            {
                "termino": "Hipertensión",
                "definicion": "Presión arterial elevada",
                "causas": "Obesidad, sedentarismo, estrés",
                "tratamientos": "Medicación antihipertensiva, dieta, ejercicio"
            }
        
        Response:
            201: Término creado
            400: Datos inválidos
            403: No es administrador
        """
        serializer = DiccionarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            new_id = sp_diccionario_create(**serializer.validated_data)
            data = sp_diccionario_get(new_id)
            
            return Response(
                data,
                status=status.HTTP_201_CREATED
            )
            
        except (OperationalError, DatabaseError) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, pk=None):
        """
        PUT /api/diccionario/:id/
        
        Actualiza un término existente en el diccionario.
        
        Permiso: Solo Administradores
        
        Args:
            pk: ID del término
        
        Request Body:
            {
                "id_usuario_admin": 3,
                "termino": "Hipertensión",
                "definicion": "Presión arterial elevada (actualizado)",
                "causas": "...",
                "tratamientos": "..."
            }
        
        Response:
            200: Término actualizado
            404: Término no encontrado
            403: No es administrador
        """
        serializer = DiccionarioUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            rows = sp_diccionario_update(
                serializer.validated_data["id_usuario_admin"],
                int(pk),
                serializer.validated_data["termino"],
                serializer.validated_data["definicion"],
                serializer.validated_data["causas"],
                serializer.validated_data["tratamientos"],
            )
            
            if rows == 0:
                return Response(
                    {"detail": "Término no encontrado o sin cambios."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            data = sp_diccionario_get(int(pk))
            return Response(data, status=status.HTTP_200_OK)
            
        except (OperationalError, DatabaseError) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, pk=None):
        """
        DELETE /api/diccionario/:id/?id_usuario_admin=X
        
        Elimina un término del diccionario.
        
        Permiso: Solo Administradores
        
        Args:
            pk: ID del término
        
        Query Params:
            id_usuario_admin: ID del administrador que elimina
        
        Response:
            200: Término eliminado
            400: Falta id_usuario_admin
            404: Término no encontrado
            403: No es administrador
        """
        id_usuario_admin = request.query_params.get("id_usuario_admin")
        
        if not id_usuario_admin:
            return Response(
                {
                    "detail": "Se requiere el parámetro 'id_usuario_admin' en la URL.",
                    "hint": "Agrega ?id_usuario_admin=X a la URL"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rows = sp_diccionario_delete(int(id_usuario_admin), int(pk))
            
            if rows == 0:
                return Response(
                    {"detail": "Término no encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": "Término eliminado correctamente del diccionario."},
                status=status.HTTP_200_OK
            )
            
        except (OperationalError, DatabaseError) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - list/retrieve/search: AllowAny (público)
#    - create/update/destroy: IsAdministrador
#
# 2. USO EDUCATIVO:
#    - Pacientes buscan términos médicos que no entienden
#    - Aprenden sobre enfermedades, causas y tratamientos
#    - Mejora comunicación médico-paciente
#
# 3. GESTIÓN:
#    - Admin mantiene diccionario actualizado
#    - Agrega términos comunes en la práctica
#    - Actualiza con nuevos tratamientos
#
# =============================================================================