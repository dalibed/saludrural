from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import DatabaseError

from .serializers import (
    CrearCitaSerializer,
    CancelarCitaSerializer,
    CitaSerializer
)
from .services import (
    sp_cita_create,
    sp_cita_cancelar,
    sp_cita_list_paciente,
    sp_cita_list_medico,
    sp_cita_completar
)


class CitaViewSet(viewsets.ViewSet):

    # POST /api/citas/
    def create(self, request):
        serializer = CrearCitaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            id_cita = sp_cita_create(
                data["id_usuario_paciente"],
                data["id_usuario_medico"],
                data["id_agenda"],
                data["motivo_consulta"]
            )
        except DatabaseError as e:
            msg = str(e).lower()

            if "no está registrado como paciente" in msg:
                return Response({"detail": "El usuario no está registrado como paciente."}, 404)

            if "paciente está desactivado" in msg:
                return Response({"detail": "El paciente está desactivado."}, 403)

            if "no está registrado como médico" in msg:
                return Response({"detail": "El usuario no está registrado como médico."}, 404)

            if "médico está desactivado" in msg:
                return Response({"detail": "El médico está desactivado."}, 403)

            if "médico no está aprobado" in msg:
                return Response({"detail": "El médico no está aprobado para recibir citas."}, 403)

            if "ya no está disponible" in msg:
                return Response({"detail": "Este horario ya no está disponible."}, 400)

            if "no se pueden crear citas en el pasado" in msg:
                return Response({"detail": "No se pueden crear citas en el pasado."}, 400)

            if "ya tiene una cita programada" in msg:
                return Response({"detail": "El paciente ya tiene una cita programada a esa hora."}, 400)

            if "no pertenece a este médico" in msg:
                return Response({"detail": "La franja horaria no pertenece a este médico."}, 403)

            return Response({"detail": str(e)}, 400)

        return Response({"detail": "Cita creada correctamente.", "id_cita": id_cita}, 201)

    # PUT /api/citas/cancelar/<id_cita>/
    def cancelar(self, request, pk=None):
        serializer = CancelarCitaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            afectadas = sp_cita_cancelar(int(pk), data["id_usuario"], data.get("motivo_cancelacion", ""))
        except DatabaseError as e:
            msg = str(e).lower()

            if "cita no existe" in msg:
                return Response({"detail": "La cita no existe."}, 404)

            if "ya está cancelada" in msg:
                return Response({"detail": "La cita ya está cancelada."}, 400)

            if "no se puede cancelar una cita completada" in msg:
                return Response({"detail": "No se puede cancelar una cita completada."}, 400)

            if "no tiene permisos" in msg:
                return Response({"detail": "No tiene permisos para cancelar esta cita."}, 403)

            return Response({"detail": str(e)}, 400)

        return Response({"detail": "Cita cancelada correctamente.", "filas_afectadas": afectadas})

    # ➤ NUEVO MÉTODO
    # PUT /api/citas/completar/<id_cita>/
    def completar(self, request, pk=None):
        id_usuario_medico = request.data.get("id_usuario_medico")

        if not id_usuario_medico:
            return Response({"detail": "Debe enviar id_usuario_medico."}, 400)

        try:
            mensaje = sp_cita_completar(
                int(id_usuario_medico),
                int(pk)
            )
        except DatabaseError as e:
            msg = str(e).lower()

            if "no está registrado como médico" in msg:
                return Response({"detail": "El usuario no está registrado como médico."}, 404)

            if "médico está desactivado" in msg:
                return Response({"detail": "El médico está desactivado."}, 403)

            if "médico no está aprobado" in msg:
                return Response({"detail": "El médico no está aprobado."}, 403)

            if "cita no existe" in msg:
                return Response({"detail": "La cita no existe."}, 404)

            if "solo el médico asignado" in msg:
                return Response({"detail": "Solo el médico asignado puede completar la cita."}, 403)

            if "ya está completada" in msg:
                return Response({"detail": "La cita ya está completada."}, 400)

            if "no se puede completar una cita cancelada" in msg:
                return Response({"detail": "No se puede completar una cita cancelada."}, 400)

            return Response({"detail": str(e)}, 400)

        return Response({"detail": mensaje}, 200)

    # GET /api/citas/paciente/<id_usuario>/
    def citas_paciente(self, request, pk=None):
        try:
            rows = sp_cita_list_paciente(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()
            if "no está registrado como paciente" in msg:
                return Response({"detail": "El usuario no está registrado como paciente."}, 404)
            return Response({"detail": str(e)}, 400)

        return Response(rows, 200)

    # GET /api/citas/medico/<id_usuario>/
    def citas_medico(self, request, pk=None):
        try:
            rows = sp_cita_list_medico(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()
            if "no está registrado como médico" in msg:
                return Response({"detail": "El usuario no está registrado como médico."}, 404)
            return Response({"detail": str(e)}, 400)

        return Response(rows, 200)

