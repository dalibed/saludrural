from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import DatabaseError

from .serializers import AntecedentesUpdateSerializer
from .services import (
    sp_historia_clinica_get_by_paciente,
    sp_historia_clinica_update_antecedentes,
    sp_historia_completa_by_paciente,
)


class HistoriaClinicaViewSet(viewsets.ViewSet):
    """
    Módulo HISTORIA CLÍNICA (base)

    - GET  /api/historia/paciente/<id_usuario_paciente>/
    - PUT  /api/historia/antecedentes/<id_usuario_medico>/<id_usuario_paciente>/
    - GET  /api/historia/completa/<id_usuario_medico>/<id_usuario_paciente>/
    """

    # GET /api/historia/paciente/<id_usuario_paciente>/
    def historia_paciente(self, request, pk=None):
        try:
            data = sp_historia_clinica_get_by_paciente(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()
            if "no está registrado como paciente" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como paciente."},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not data:
            return Response(
                {"detail": "Historia clínica no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(data, status=status.HTTP_200_OK)

    # PUT /api/historia/antecedentes/<id_usuario_medico>/<id_usuario_paciente>/
    def actualizar_antecedentes(self, request, id_medico=None, id_paciente=None):
        serializer = AntecedentesUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        antecedentes = serializer.validated_data["antecedentes"]

        try:
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
                    {"detail": "El médico está desactivado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if "médico no está aprobado" in msg:
                return Response(
                    {"detail": "El médico no está aprobado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if "paciente no existe" in msg:
                return Response(
                    {"detail": "El paciente no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            if "historia clínica no existe" in msg:
                return Response(
                    {"detail": "La historia clínica no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if filas == 0:
            return Response(
                {"detail": "No se actualizó ningún registro."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"detail": "Antecedentes actualizados correctamente.", "filas_afectadas": filas},
            status=status.HTTP_200_OK
        )

    # GET /api/historia/completa/<id_usuario_medico>/<id_usuario_paciente>/
    def historia_completa(self, request, id_medico=None, id_paciente=None):
        try:
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
                    {"detail": "El médico está desactivado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if "médico no está aprobado" in msg:
                return Response(
                    {"detail": "El médico no está aprobado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if "paciente no existe" in msg:
                return Response(
                    {"detail": "El paciente no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not data.get("historia"):
            return Response(
                {"detail": "Historia clínica no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(data, status=status.HTTP_200_OK)
