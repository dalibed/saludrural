from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import OperationalError, DatabaseError

from .serializers import (
    DiccionarioCreateSerializer,
    DiccionarioUpdateSerializer,
)

from .services import (
    sp_diccionario_create,
    sp_diccionario_update,
    sp_diccionario_delete,
    sp_diccionario_get,
    sp_diccionario_list,
    sp_diccionario_search,
)


class DiccionarioViewSet(viewsets.ViewSet):

    def list(self, request):
        data = sp_diccionario_list()
        return Response(data, status=200)

    def retrieve(self, request, pk=None):
        data = sp_diccionario_get(int(pk))
        if not data:
            return Response({"detail": "No encontrado"}, status=404)
        return Response(data, status=200)

    def create(self, request):
        serializer = DiccionarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            new_id = sp_diccionario_create(**serializer.validated_data)
            data = sp_diccionario_get(new_id)
            return Response(data, status=201)

        except (OperationalError, DatabaseError) as e:
            return Response({"error": str(e)}, status=400)

    def update(self, request, pk=None):
        serializer = DiccionarioUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            rows = sp_diccionario_update(
                serializer.validated_data["id_usuario_admin"],
                int(pk),
                serializer.validated_data["termino"],
                serializer.validated_data["definicion"],
                serializer.validated_data["causas"],
                serializer.validated_data["tratamientos"],
            )

            if rows == 0:
                return Response({"detail": "No se actualizó ningún registro"}, status=404)

            data = sp_diccionario_get(int(pk))
            return Response(data, status=200)

        except (OperationalError, DatabaseError) as e:
            return Response({"error": str(e)}, status=400)

    def destroy(self, request, pk=None):
        id_usuario_admin = request.query_params.get("id_usuario_admin")

        if not id_usuario_admin:
            return Response({"detail": "Se requiere id_usuario_admin"}, status=400)

        try:
            rows = sp_diccionario_delete(int(id_usuario_admin), int(pk))

            if rows == 0:
                return Response({"detail": "No se eliminó ningún registro"}, status=404)

            return Response({"mensaje": "Eliminado con éxito"}, status=200)

        except (OperationalError, DatabaseError) as e:
            return Response({"error": str(e)}, status=400)

    def search(self, request):
        busqueda = request.query_params.get("q", "")
        results = sp_diccionario_search(busqueda)
        return Response(results, status=200)
