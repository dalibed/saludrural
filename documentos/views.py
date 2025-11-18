from django.db import DatabaseError
from rest_framework import status, viewsets
from rest_framework.response import Response

from .serializers import (
    DocumentoUploadSerializer,
    DocumentoSerializer,
    DocumentoValidacionSerializer,
)
from .services import (
    sp_documento_upload,
    sp_documento_validate,
    sp_documento_list_by_usuario,
)


class DocumentoViewSet(viewsets.ViewSet):
    """
    Módulo: Documentos

    - El médico (ID_Usuario) sube documentos.
    - El administrador valida documentos.
    - Todo se maneja por stored procedures.
    """

    # GET /api/documentos/?id_usuario_medico=XX
    def list(self, request):
        id_usuario_medico = request.query_params.get("id_usuario_medico")

        if not id_usuario_medico:
            return Response(
                {"detail": "Se requiere el parámetro 'id_usuario_medico' en la URL."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            docs = sp_documento_list_by_usuario(int(id_usuario_medico))
        except DatabaseError as e:
            msg = str(e).lower()

            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Los nombres de columnas vienen tal cual del SP
        # Mapeamos a DocumentoSerializer si queremos estandarizar
        data = []
        for d in docs:
            data.append({
                "id_documento": d["ID_Documento"],
                "archivo": d["Archivo"],
                "fecha_subida": d["FechaSubida"],
                "estado": d["Estado"],
                "id_tipo_documento": d["ID_TipoDocumento"],
                "tipo_documento": d["TipoDocumento"],
                "descripcion": d["Descripcion"],
            })

        serializer = DocumentoSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=False)  # Solo para asegurar formato

        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST /api/documentos/
    def create(self, request):
        serializer = DocumentoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_usuario_medico = serializer.validated_data["id_usuario_medico"]
        id_tipo_documento = serializer.validated_data["id_tipo_documento"]
        archivo = serializer.validated_data["archivo"]

        try:
            nuevo_id = sp_documento_upload(
                id_usuario_medico=id_usuario_medico,
                id_tipo_documento=id_tipo_documento,
                archivo=archivo,
            )
        except DatabaseError as e:
            msg = str(e).lower()

            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if "está desactivado" in msg and "médico" in msg:
                return Response(
                    {"detail": "El médico está desactivado. No puede subir documentos."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if "tipo de documento no existe" in msg:
                return Response(
                    {"detail": "El tipo de documento no existe."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # No tenemos un SP de "get documento por ID", así que devolvemos el ID creado
        return Response(
            {
                "id_documento": nuevo_id,
                "detail": "Documento subido correctamente y marcado como Pendiente."
            },
            status=status.HTTP_201_CREATED,
        )

    # POST /api/documentos/<pk>/validar/
    # pk = ID_Documento
    def validate(self, request, pk=None):
        serializer = DocumentoValidacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        estado = serializer.validated_data["estado"]
        observaciones = serializer.validated_data["observaciones"]
        id_usuario_admin = serializer.validated_data["id_usuario_admin"]

        try:
            resultado = sp_documento_validate(
                id_documento=int(pk),
                estado=estado,
                observaciones=observaciones,
                id_usuario_admin=id_usuario_admin,
            )
        except DatabaseError as e:
            msg = str(e).lower()

            if "no está registrado como administrador" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como administrador."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if "documento no existe" in msg:
                return Response(
                    {"detail": "El documento no existe."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not resultado:
            # SP debería siempre devolver algo, pero por seguridad:
            return Response(
                {"detail": "No se pudo obtener el resultado de la validación."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(resultado, status=status.HTTP_200_OK)
