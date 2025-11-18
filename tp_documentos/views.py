from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import DatabaseError

from .serializers import (
    TipoDocCreateSerializer,
    TipoDocUpdateSerializer,
    TipoDocSerializer
)
from .services import (
    sp_tipodoc_create,
    sp_tipodoc_update,
    sp_tipodoc_delete,
    sp_tipodoc_get,
    sp_tipodoc_list
)


class TipoDocumentoViewSet(viewsets.ViewSet):

    # POST /api/tipodocumento/
    def create(self, request):
        serializer = TipoDocCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            new_id = sp_tipodoc_create(
                serializer.validated_data["nombre"],
                serializer.validated_data.get("descripcion", "")
            )
        except DatabaseError as e:
            return Response({"detail": str(e)}, 400)

        obj = sp_tipodoc_get(new_id)
        return Response(obj, 201)


    # GET /api/tipodocumento/
    def list(self, request):
        data = sp_tipodoc_list()
        return Response(data, 200)


    # GET /api/tipodocumento/<id>/
    def retrieve(self, request, pk=None):
        obj = sp_tipodoc_get(int(pk))

        if not obj:
            return Response({"detail": "Tipo de documento no encontrado."}, 404)

        return Response(obj, 200)


    # PUT /api/tipodocumento/<id>/
    def update(self, request, pk=None):
        serializer = TipoDocUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            filas = sp_tipodoc_update(
                int(pk),
                serializer.validated_data["nombre"],
                serializer.validated_data["descripcion"],
            )
        except DatabaseError as e:
            return Response({"detail": str(e)}, 400)

        if filas == 0:
            return Response({"detail": "Tipo de documento no encontrado."}, 404)

        obj = sp_tipodoc_get(int(pk))
        return Response(obj, 200)


    # DELETE /api/tipodocumento/<id>/
    def destroy(self, request, pk=None):
        try:
            filas = sp_tipodoc_delete(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()
            if "tiene documentos asociados" in msg:
                return Response(
                    {"detail": "No se puede eliminar el tipo porque tiene documentos asociados."},
                    400
                )
            return Response({"detail": str(e)}, 400)

        if filas == 0:
            return Response({"detail": "Tipo de documento no encontrado."}, 404)

        return Response({"detail": "Eliminado correctamente."}, 200)
