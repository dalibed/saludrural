"""
Views para el módulo de Tipos de Documentos

Gestiona el catálogo de tipos de documentos requeridos para validación médica.
Con PERMISOS implementados.

Lógica de permisos:
- Listar/ver tipos: Público (médicos ven qué documentos necesitan)
- Crear/actualizar/eliminar: Solo Admin
"""

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import DatabaseError

from backend.permissions import IsAdministrador

from .serializers import (
    TipoDocCreateSerializer,
    TipoDocUpdateSerializer,
    TipoDocSerializer
)
from .services import (
    sp_tipodoc_create,
    sp_tipodoc_update,
    sp_tipodoc_delete,
    sp_tipodoc_get,
    sp_tipodoc_list
)


class TipoDocumentoViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de Tipos de Documentos.
    
    Endpoints:
    - GET    /api/tipodocumento/       → Listar tipos (público)
    - GET    /api/tipodocumento/:id/   → Ver tipo (público)
    - POST   /api/tipodocumento/       → Crear tipo (admin)
    - PUT    /api/tipodocumento/:id/   → Actualizar tipo (admin)
    - DELETE /api/tipodocumento/:id/   → Eliminar tipo (admin)
    
    Permisos:
    - list/retrieve: Público (médicos ven qué documentos necesitan)
    - create/update/destroy: Solo Administradores
    """
    
    def get_permissions(self):
        """
        Define permisos según la acción.
        
        - Lectura: Público
        - Escritura: Solo Admin
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdministrador()]
    
    # =========================================================================
    # ENDPOINTS PÚBLICOS (Información para médicos)
    # =========================================================================
    
    def list(self, request):
        """
        GET /api/tipodocumento/
        
        Lista todos los tipos de documentos requeridos.
        
        Permiso: Público
        
        Uso: Médicos ven qué documentos deben subir para validación
        
        Response:
            200: Lista de tipos
            [
                {
                    "ID_TipoDocumento": 1,
                    "Nombre": "Título Profesional",
                    "Descripcion": "Título universitario de medicina"
                },
                {
                    "ID_TipoDocumento": 2,
                    "Nombre": "Licencia Médica",
                    "Descripcion": "Licencia para ejercer medicina"
                }
            ]
        """
        data = sp_tipodoc_list()
        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """
        GET /api/tipodocumento/:id/
        
        Obtiene un tipo de documento específico.
        
        Permiso: Público
        
        Args:
            pk: ID del tipo de documento
        
        Response:
            200: Datos del tipo
            404: Tipo no encontrado
        """
        obj = sp_tipodoc_get(int(pk))
        
        if not obj:
            return Response(
                {"detail": "Tipo de documento no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(obj, status=status.HTTP_200_OK)
    
    # =========================================================================
    # ENDPOINTS DE ADMINISTRACIÓN
    # =========================================================================
    
    def create(self, request):
        """
        POST /api/tipodocumento/
        
        Crea un nuevo tipo de documento.
        
        Permiso: Solo Administradores
        
        Request Body:
            {
                "nombre": "Certificado de Especialidad",
                "descripcion": "Certificado que acredita la especialidad médica"
            }
        
        Response:
            201: Tipo creado
            400: Datos inválidos
            403: No es administrador
        """
        serializer = TipoDocCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            new_id = sp_tipodoc_create(
                serializer.validated_data["nombre"],
                serializer.validated_data.get("descripcion", "")
            )
            
        except DatabaseError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        obj = sp_tipodoc_get(new_id)
        return Response(obj, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """
        PUT /api/tipodocumento/:id/
        
        Actualiza un tipo de documento existente.
        
        Permiso: Solo Administradores
        
        Args:
            pk: ID del tipo de documento
        
        Request Body:
            {
                "nombre": "Certificado de Especialidad (actualizado)",
                "descripcion": "Descripción actualizada"
            }
        
        Response:
            200: Tipo actualizado
            404: Tipo no encontrado
            403: No es administrador
        """
        serializer = TipoDocUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            filas = sp_tipodoc_update(
                int(pk),
                serializer.validated_data["nombre"],
                serializer.validated_data["descripcion"],
            )
            
        except DatabaseError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if filas == 0:
            return Response(
                {"detail": "Tipo de documento no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        obj = sp_tipodoc_get(int(pk))
        return Response(obj, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        """
        DELETE /api/tipodocumento/:id/
        
        Elimina un tipo de documento.
        
        Permiso: Solo Administradores
        
        Args:
            pk: ID del tipo de documento
        
        Response:
            200: Tipo eliminado
            400: Tiene documentos asociados (no se puede eliminar)
            404: Tipo no encontrado
            403: No es administrador
        """
        try:
            filas = sp_tipodoc_delete(int(pk))
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "tiene documentos asociados" in msg:
                return Response(
                    {
                        "detail": "No se puede eliminar el tipo porque tiene documentos asociados.",
                        "hint": "Primero elimina o cambia el tipo de los documentos asociados."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if filas == 0:
            return Response(
                {"detail": "Tipo de documento no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {"detail": "Tipo de documento eliminado correctamente."},
            status=status.HTTP_200_OK
        )


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - list/retrieve: AllowAny (público)
#    - create/update/destroy: IsAdministrador
#
# 2. USO TÍPICO:
#    - Médico registrado ve qué documentos debe subir
#    - Admin gestiona catálogo de tipos requeridos
#    - Sistema valida que médico tenga todos los tipos
#
# 3. TIPOS COMUNES:
#    - Título Profesional
#    - Licencia Médica
#    - Certificado de Especialidad
#    - Cédula Profesional
#    - RUT (Registro Único Tributario)
#
# 4. INTEGRIDAD:
#    - No se pueden eliminar tipos con documentos asociados
#    - Mantiene consistencia referencial
#
# =============================================================================