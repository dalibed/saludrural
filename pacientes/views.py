from django.db import DatabaseError
from rest_framework import status, viewsets
from rest_framework.response import Response

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
    Módulo: Pacientes

    - El registro base se crea cuando se crea el Usuario con rol 'Paciente'.
    - Aquí solo se gestionan datos clínicos / de contacto.
    """

    # GET /api/pacientes/
    def list(self, request):
        data = sp_paciente_list()
        return Response(data, status=status.HTTP_200_OK)

    # GET /api/pacientes/<pk>/
    # pk = ID_Usuario del paciente
    def retrieve(self, request, pk=None):
        paciente = sp_paciente_get_by_usuario(int(pk))
        if not paciente:
            return Response(
                {"detail": "Paciente no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(paciente, status=status.HTTP_200_OK)

    # PUT /api/pacientes/<pk>/
    def update(self, request, pk=None):
        serializer = PacienteUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            sp_paciente_update(int(pk), **serializer.validated_data)
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
            if "el paciente no existe" in msg:
                return Response(
                    {"detail": "El paciente no existe."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        paciente = sp_paciente_get_by_usuario(int(pk))
        return Response(paciente, status=status.HTTP_200_OK)
