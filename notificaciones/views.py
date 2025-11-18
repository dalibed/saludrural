from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import DatabaseError

from .services import (
    sp_notificacion_list_paciente,
    sp_notificacion_list_medico
)


class NotificacionViewSet(viewsets.ViewSet):

    # GET /api/notificaciones/paciente/<id_usuario>/
    def list_paciente(self, request, pk=None):
        try:
            data = sp_notificacion_list_paciente(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()

            if "paciente no existe" in msg:
                return Response({"detail": "El paciente no existe."}, 404)

            return Response({"detail": str(e)}, 400)

        return Response(data, 200)

    # GET /api/notificaciones/medico/<id_usuario>/
    def list_medico(self, request, pk=None):
        try:
            data = sp_notificacion_list_medico(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()

            if "médico no existe" in msg:
                return Response({"detail": "El médico no existe."}, 404)

            return Response({"detail": str(e)}, 400)

        return Response(data, 200)
