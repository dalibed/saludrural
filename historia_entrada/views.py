from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import DatabaseError

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
    Módulo HISTORIA_ENTRADA

    - POST /api/historia-entradas/
    - PUT  /api/historia-entradas/<id_entrada>/
    - GET  /api/historia-entradas/<id_entrada>/
    - GET  /api/historia/entrada/paciente/<id_usuario_paciente>/
    - GET  /api/historia/entrada/medico/<id_usuario_medico>/
    """

    # POST /api/historia-entradas/
    def create(self, request):
        serializer = HistoriaEntradaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            id_entrada = sp_historia_entrada_create(
                data["id_usuario_medico"],
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
                    {"detail": "El médico está desactivado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if "médico no está aprobado" in msg:
                return Response(
                    {"detail": "El médico no está aprobado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if "cita no existe" in msg:
                return Response(
                    {"detail": "La cita no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            if "solo se puede crear entrada de historia para citas completadas" in msg:
                return Response(
                    {"detail": "Solo se puede crear entrada de historia para citas completadas."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if "solo el médico asignado a la cita puede crear la entrada" in msg:
                return Response(
                    {"detail": "Solo el médico asignado a la cita puede crear la entrada."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if "ya existe una entrada de historia para esta cita" in msg:
                return Response(
                    {"detail": "Ya existe una entrada de historia para esta cita."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if "no tiene historia clínica" in msg:
                return Response(
                    {"detail": "El paciente no tiene historia clínica."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"detail": "Entrada de historia creada correctamente.", "id_entrada": id_entrada},
            status=status.HTTP_201_CREATED
        )

    # PUT /api/historia-entradas/<id_entrada>/
    def update(self, request, pk=None):
        serializer = HistoriaEntradaUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            filas = sp_historia_entrada_update(
                data["id_usuario_medico"],
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
                    {"detail": "El médico está desactivado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if "médico no está aprobado" in msg:
                return Response(
                    {"detail": "El médico no está aprobado."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if "entrada de historia no existe" in msg:
                return Response(
                    {"detail": "La entrada de historia no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            if "solo el médico que creó la entrada puede modificarla" in msg:
                return Response(
                    {"detail": "Solo el médico que creó la entrada puede modificarla."},
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if filas == 0:
            return Response(
                {"detail": "Entrada de historia no encontrada o sin cambios."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"detail": "Entrada de historia actualizada correctamente.", "filas_afectadas": filas},
            status=status.HTTP_200_OK
        )

    # GET /api/historia-entradas/<id_entrada>/
    def retrieve(self, request, pk=None):
        try:
            data = sp_historia_entrada_get(int(pk))
        except DatabaseError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not data:
            return Response(
                {"detail": "Entrada de historia no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(data, status=status.HTTP_200_OK)

    # GET /api/historia/entrada/paciente/<id_usuario_paciente>/
    def list_paciente(self, request, pk=None):
        try:
            data = sp_historia_entrada_list_by_paciente(int(pk))
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

            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)

    # GET /api/historia/entrada/medico/<id_usuario_medico>/
    def list_medico(self, request, pk=None):
        try:
            data = sp_historia_entrada_list_by_medico(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()

            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_200_OK)
