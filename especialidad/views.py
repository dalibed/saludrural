from rest_framework import status, viewsets
from rest_framework.response import Response
from django.db import DatabaseError

from .serializers import (
    EspecialidadCreateSerializer,
    AsignarEspecialidadSerializer
)
from .services import (
    sp_especialidad_create,
    sp_especialidad_list,
    sp_medico_especialidad_asignar,
    sp_medico_especialidad_list
)


class EspecialidadViewSet(viewsets.ViewSet):

    # POST /api/especialidades/
    def create(self, request):
        serializer = EspecialidadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            new_id = sp_especialidad_create(data["nombre"], data["descripcion"])
        except DatabaseError as e:
            msg = str(e).lower()

            if "ya existe" in msg:
                return Response({"detail": "La especialidad ya existe."}, 400)

            return Response({"detail": str(e)}, 400)

        return Response(
            {"detail": "Especialidad creada correctamente.", "id_especialidad": new_id},
            201
        )

    # GET /api/especialidades/
    def list(self, request):
        rows = sp_especialidad_list()
        return Response(rows, 200)

    # POST /api/especialidades/asignar/
    def asignar(self, request):
        serializer = AsignarEspecialidadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            affected = sp_medico_especialidad_asignar(
                data["id_usuario_medico"],
                data["id_especialidad"]
            )
        except DatabaseError as e:
            msg = str(e).lower()

            if "médico no existe" in msg:
                return Response({"detail": "El médico no existe."}, 404)

            if "especialidad no existe" in msg:
                return Response({"detail": "La especialidad no existe."}, 404)

            return Response({"detail": str(e)}, 400)

        return Response(
            {"detail": "Especialidad asignada correctamente.", "filas_afectadas": affected},
            200
        )

    # GET /api/especialidades/medico/<id_usuario_medico>/
    def listar_por_medico(self, request, pk=None):
        try:
            rows = sp_medico_especialidad_list(int(pk))
        except DatabaseError as e:
            msg = str(e).lower()
            if "médico no existe" in msg:
                return Response({"detail": "El médico no existe."}, 404)

            return Response({"detail": str(e)}, 400)

        return Response(rows, 200)
