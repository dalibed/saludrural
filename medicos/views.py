from django.db import DatabaseError
from rest_framework import status, viewsets
from rest_framework.response import Response

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
    Módulo: Médicos

    - El registro básico del médico se crea desde sp_usuario_create (rol 'Medico').
    - Aquí se gestiona:
        * Perfil profesional
        * Listados
        * Estado de validación
    """

    # GET /api/medicos/
    def list(self, request):
        data = sp_medico_list()
        return Response(data, status=status.HTTP_200_OK)

    # GET /api/medicos/<pk>/
    # pk = ID_Usuario del médico
    def retrieve(self, request, pk=None):
        medico = sp_medico_get_by_usuario(int(pk))
        if not medico:
            return Response(
                {"detail": "Médico no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(medico, status=status.HTTP_200_OK)

    # PUT /api/medicos/<pk>/
    def update(self, request, pk=None):
        serializer = MedicoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            sp_medico_update(int(pk), **serializer.validated_data)
        except DatabaseError as e:
            msg = str(e).lower()

            if "el usuario no existe" in msg:
                return Response(
                    {"detail": "El usuario no existe."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if "está desactivado" in msg:
                return Response(
                    {"detail": "El usuario está desactivado. No se permiten cambios."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if "no existe médico" in msg:
                return Response(
                    {"detail": "No existe médico asociado a este usuario."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        medico = sp_medico_get_by_usuario(int(pk))
        return Response(medico, status=status.HTTP_200_OK)

    # GET /api/medicos/listar-estado/<estado>/
    def list_by_estado(self, request, estado=None):
        data = sp_medico_list_by_estado(estado)
        return Response(data, status=status.HTTP_200_OK)

    # GET /api/medicos/estado/<pk>/
    # pk = ID_Usuario del médico
    def estado(self, request, pk=None):
        try:
            data = sp_medico_estado(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()

            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if "está desactivado" in msg:
                return Response(
                    {"detail": "El usuario está desactivado. No se permiten cambios."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not data:
            return Response(
                {"detail": "Médico no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(data, status=status.HTTP_200_OK)

