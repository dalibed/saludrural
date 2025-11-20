"""
Views para el módulo de Pacientes

Gestiona perfiles clínicos de pacientes.
Con PERMISOS para proteger datos personales.
"""

from django.db import DatabaseError
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.permissions import IsAdministrador

from .serializers import (
    PacienteUpdateSerializer,
)
from .services import (
    sp_paciente_list,
    sp_paciente_get_by_usuario,
    sp_paciente_update,
)


class PacienteViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de perfiles de Pacientes.
    
    Permisos:
    - list: Solo Admin
    - retrieve: Paciente ve solo su perfil, Médico/Admin ven todos
    - update: Paciente actualiza solo su perfil, Admin actualiza todos
    """
    
    def get_permissions(self):
        if self.action == 'list':
            return [IsAdministrador()]
        return [IsAuthenticated()]
    
    def list(self, request):
        """GET /api/pacientes/ - Solo Admin"""
        data = sp_paciente_list()
        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """GET /api/pacientes/:id/ - Propio perfil o Admin"""
        # Validación ownership
        if request.user.rol == 'Paciente':
            from pacientes.models import Paciente
            try:
                paciente = Paciente.objects.get(id_usuario=request.user.id_usuario)
                if paciente.id_usuario != int(pk):
                    return Response(
                        {"detail": "No tienes permiso para ver otros perfiles."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Paciente.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        paciente = sp_paciente_get_by_usuario(int(pk))
        if not paciente:
            return Response(
                {"detail": "Paciente no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(paciente, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        """PUT /api/pacientes/:id/ - Propio perfil o Admin"""
        # Validación ownership
        if request.user.rol == 'Paciente':
            from pacientes.models import Paciente
            try:
                paciente = Paciente.objects.get(id_usuario=request.user.id_usuario)
                if paciente.id_usuario != int(pk):
                    return Response(
                        {"detail": "No puedes modificar perfiles ajenos."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Paciente.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = PacienteUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            sp_paciente_update(int(pk), **serializer.validated_data)
        except DatabaseError as e:
            msg = str(e).lower()
            if "no existe" in msg:
                return Response(
                    {"detail": "Paciente no encontrado."},
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
        
        paciente = sp_paciente_get_by_usuario(int(pk))
        return Response(paciente, status=status.HTTP_200_OK)