from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import DatabaseError

from .serializers import AdminIDSerializer
from .services import sp_admin_get_id_by_usuario


class AdministradorViewSet(viewsets.ViewSet):
    """
    MÓDULO: Administrador (mínimo con el SP actual)

    - No duplica lógica de usuarios, documentos, etc.
    - Solo expone:
        GET /api/administrador/<id_usuario>/
        Para saber si un usuario es administrador y obtener su ID_Admin.
    """

    # GET /api/administrador/<id_usuario>/
    def retrieve(self, request, pk=None):
        try:
            id_admin = sp_admin_get_id_by_usuario(int(pk))
        except DatabaseError as e:
            # Si ocurre un error de base de datos inesperado
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        if id_admin is None:
            return Response(
                {"detail": "El usuario no está registrado como administrador."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = {"id_admin": id_admin}
        serializer = AdminIDSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
