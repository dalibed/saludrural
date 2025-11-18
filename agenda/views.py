from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import DatabaseError

from .serializers import (
    AgendaCreateRangeSerializer,
    AgendaToggleSerializer,
    AgendaSerializer
)
from .services import (
    sp_agenda_create_range,
    sp_agenda_toggle_slot,
    sp_agenda_list_by_usuario,
    sp_agenda_list_disponible_by_usuario
)


class AgendaViewSet(viewsets.ViewSet):

    # POST /api/agendas/
    def create(self, request):
        serializer = AgendaCreateRangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            creados = sp_agenda_create_range(
                serializer.validated_data["id_usuario_medico"],
                serializer.validated_data["fecha"],
                serializer.validated_data["hora_inicio"],
                serializer.validated_data["hora_fin"],
            )
        except DatabaseError as e:
            msg = str(e).lower()

            if "no está registrado como médico" in msg:
                return Response({"detail": "El usuario no está registrado como médico."}, 404)
            if "desactivado" in msg:
                return Response({"detail": "El médico está desactivado."}, 403)
            if "documentación aprobada" in msg:
                return Response({"detail": "El médico no tiene toda la documentación aprobada."}, 403)
            if "no está validado" in msg:
                return Response({"detail": "El médico no está validado para crear agenda."}, 403)
            if "fechas pasadas" in msg:
                return Response({"detail": "No se puede crear agenda en fechas pasadas."}, 400)
            if "horarios deben estar" in msg:
                return Response({"detail": "Los horarios deben estar entre 06:00 y 22:00."}, 400)
            if "hora fin" in msg:
                return Response({"detail": "La hora fin debe ser mayor que la hora inicio."}, 400)

            return Response({"detail": str(e)}, 400)

        return Response(
            {"detail": "Agenda creada correctamente.", "slots_creados": creados},
            status=201
        )

    # GET /api/agendas/<id_usuario_medico>/
    def retrieve(self, request, pk=None):
        try:
            rows = sp_agenda_list_by_usuario(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()
            if "no está registrado como médico" in msg:
                return Response({"detail": "El usuario no está registrado como médico."}, 404)
            return Response({"detail": str(e)}, 400)

        data = [
            {
                "id_agenda": r["ID_Agenda"],
                "fecha": r["Fecha"],
                "hora": r["Hora"],
                "disponible": bool(r["Disponible"]),
            }
            for r in rows
        ]

        return Response(data, 200)

    # GET /api/agendas/disponible/<id_usuario_medico>/
    def disponible(self, request, pk=None):
        try:
            rows = sp_agenda_list_disponible_by_usuario(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()
            if "no está registrado como médico" in msg:
                return Response({"detail": "El usuario no está registrado como médico."}, 404)
            return Response({"detail": str(e)}, 400)

        data = [
            {
                "id_agenda": r["ID_Agenda"],
                "fecha": r["Fecha"],
                "hora": r["Hora"],
            }
            for r in rows
        ]

        return Response(data, 200)

    # PUT /api/agendas/toggle/<id_agenda>/
    def toggle(self, request, pk=None):
        serializer = AgendaToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_usuario = serializer.validated_data["id_usuario_medico"]
        disponible = serializer.validated_data["disponible"]

        try:
            afectadas = sp_agenda_toggle_slot(id_usuario, int(pk), disponible)
        except DatabaseError as e:
            msg = str(e).lower()

            if "no está registrado como médico" in msg:
                return Response({"detail": "El usuario no está registrado como médico."}, 404)
            if "no pertenece a este médico" in msg:
                return Response({"detail": "La franja de agenda no pertenece a este médico."}, 403)

            return Response({"detail": str(e)}, 400)

        return Response({"detail": "Estado actualizado.", "filas_afectadas": afectadas}, 200)
