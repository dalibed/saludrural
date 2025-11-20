"""
Views para el módulo de Médicos

Gestiona perfiles profesionales de médicos.
Con PERMISOS para proteger datos profesionales.
"""

from django.db import DatabaseError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from backend.permissions import IsMedico, IsAdministrador

from .serializers import (
    MedicoUpdateSerializer,
)
from .services import (
    sp_medico_get_by_usuario,
    sp_medico_list,
    sp_medico_list_by_estado,
    sp_medico_update,
    sp_medico_estado,
)


class MedicoViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de perfiles de Médicos.
    
    Permisos:
    - list/list_by_estado: Público (pacientes buscan médicos)
    - retrieve: Público (pacientes ven perfiles)
    - update: Médico actualiza solo su perfil, Admin todos
    - estado: Público o autenticado
    """
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'list_by_estado', 'estado']:
            return [AllowAny()]  # Público para que pacientes busquen médicos
        return [IsAuthenticated()]
    
    def list(self, request):
        """GET /api/medicos/ - Público"""
        data = sp_medico_list()
        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """GET /api/medicos/:id/ - Público"""
        medico = sp_medico_get_by_usuario(int(pk))
        if not medico:
            return Response(
                {"detail": "Médico no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(medico, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        """PUT /api/medicos/:id/ - Propio perfil o Admin"""
        # Validación ownership
        if request.user.rol == 'Medico':
            from medicos.models import Medico
            try:
                medico = Medico.objects.get(id_usuario=request.user.id_usuario)
                if medico.id_usuario.id_usuario != int(pk):
                    return Response(
                        {"detail": "No puedes modificar perfiles ajenos."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Medico.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = MedicoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            sp_medico_update(int(pk), **serializer.validated_data)
        except DatabaseError as e:
            msg = str(e).lower()
            if "no existe" in msg:
                return Response(
                    {"detail": "Médico no encontrado."},
                    status=status.HTTP_404_NOT_FOUND
                )
            if "desactivado" in msg:
                return Response(
                    {"detail": "Usuario desactivado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        medico = sp_medico_get_by_usuario(int(pk))
        return Response(medico, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='listar-estado/(?P<estado>[^/.]+)')
    def list_by_estado(self, request, estado=None):
        """GET /api/medicos/listar-estado/:estado/ - Público"""
        data = sp_medico_list_by_estado(estado)
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='estado')
    def estado(self, request, pk=None):
        """GET /api/medicos/:id/estado/ - Público"""
        try:
            data = sp_medico_estado(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()
            if "no está registrado" in msg:
                return Response(
                    {"detail": "Usuario no es médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data:
            return Response(
                {"detail": "Médico no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(data, status=status.HTTP_200_OK)
