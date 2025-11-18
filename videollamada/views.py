from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import DatabaseError

from .services import (
    sp_videollamada_crear,
    sp_videollamada_get
)


class VideollamadaViewSet(viewsets.ViewSet):

    # POST /api/videollamada/<id_cita>/
    def crear(self, request, pk=None):
        enlace = request.data.get("enlace")

        if not enlace:
            return Response({"detail": "Debe enviar un enlace."}, 400)

        try:
            mensaje = sp_videollamada_crear(
                int(pk),
                enlace
            )
        except DatabaseError as e:
            msg = str(e).lower()

            if "cita no existe" in msg:
                return Response({"detail": "La cita no existe."}, 404)

            return Response({"detail": str(e)}, 400)

        return Response({"detail": mensaje}, 200)

    # GET /api/videollamada/<id_cita>/
    def retrieve(self, request, pk=None):
        try:
            data = sp_videollamada_get(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()

            if "cita no existe" in msg:
                return Response({"detail": "La cita no existe."}, 404)

            return Response({"detail": str(e)}, 400)

        if not data:
            return Response({"detail": "La videollamada no está configurada."}, 404)

        return Response(data, 200)
