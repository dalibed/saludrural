from django.db import DatabaseError
from rest_framework import status, viewsets
from rest_framework.response import Response

from .serializers import (
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
)
from .services import (
    sp_usuario_create,
    sp_usuario_update,
    sp_usuario_get,
    sp_usuario_list,
    sp_usuario_deactivate,
    sp_usuario_activate,
)


class UsuarioViewSet(viewsets.ViewSet):
    """
    Módulo: Usuarios

    - Todo se maneja por stored procedures.
    - Creación de usuario también crea Paciente/Medico/Admin según Rol.
    """

    # GET /api/usuarios/
    def list(self, request):
        data = sp_usuario_list()
        return Response(data, status=status.HTTP_200_OK)

    # GET /api/usuarios/<pk>/
    def retrieve(self, request, pk=None):
        usuario = sp_usuario_get(int(pk))
        if not usuario:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(usuario, status=status.HTTP_200_OK)

    # POST /api/usuarios/
    def create(self, request):
        serializer = UsuarioCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            nuevo_id = sp_usuario_create(**serializer.validated_data)
        except DatabaseError as e:
            msg = str(e).lower()

            if "documento duplicado" in msg:
                return Response(
                    {"detail": "El documento ya está registrado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if "correo duplicado" in msg:
                return Response(
                    {"detail": "El correo ya está registrado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if "formato de correo inválido" in msg:
                return Response(
                    {"detail": "El formato del correo es inválido."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Cualquier otro error controlado del SP
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario = sp_usuario_get(nuevo_id)
        return Response(usuario, status=status.HTTP_201_CREATED)

    # PUT /api/usuarios/<pk>/
    def update(self, request, pk=None):
        serializer = UsuarioUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            sp_usuario_update(int(pk), **serializer.validated_data)
        except DatabaseError as e:
            msg = str(e).lower()

            if "no existe" in msg:
                return Response(
                    {"detail": "El usuario no existe."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if "desactivado" in msg:
                return Response(
                    {"detail": "El usuario está desactivado. No se permiten cambios."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if "correo ya está en uso" in msg or "correo ya está en uso por otro usuario" in msg:
                return Response(
                    {"detail": "El correo ya está en uso por otro usuario."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario = sp_usuario_get(int(pk))
        return Response(usuario, status=status.HTTP_200_OK)

    # DELETE /api/usuarios/<pk>/
    def destroy(self, request, pk=None):
        motivo = request.data.get("motivo", "Sin especificar")
        try:
            sp_usuario_deactivate(int(pk), motivo)
        except DatabaseError as e:
            msg = str(e).lower()
            if "no existe" in msg:
                return Response(
                    {"detail": "El usuario no existe."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Usuario desactivado."},
            status=status.HTTP_200_OK,
        )

    # POST /api/usuarios/<pk>/activar/
    def activate(self, request, pk=None):
        try:
            sp_usuario_activate(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()
            if "no existe" in msg:
                return Response(
                    {"detail": "El usuario no existe."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Usuario activado."},
            status=status.HTTP_200_OK,
        )
