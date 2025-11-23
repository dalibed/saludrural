"""
Views para el módulo de Documentos

Este módulo maneja la subida y validación de documentos de médicos.
Ahora con PERMISOS implementados para proteger el proceso de validación.

Lógica de permisos:
- Listar documentos (list): Médico ve solo sus docs, Admin ve todos
- Subir documento (create): Solo Médicos, solo sus propios docs
- Validar documento (validate): Solo Administradores
"""

from django.db import DatabaseError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# Importar permisos personalizados
from backend.permissions import IsMedico, IsAdministrador, IsAuthenticated

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
    ViewSet para gestión de Documentos de Médicos.
    
    Endpoints:
    - GET  /api/documentos/?id_usuario_medico=X    → Listar documentos
    - POST /api/documentos/                         → Subir documento
    - POST /api/documentos/:id/validar/             → Validar documento
    
    Permisos implementados:
    - list: Autenticado + ownership (médico solo sus docs)
    - create: Solo Médicos + ownership
    - validate: Solo Administradores
    """
    
    def get_permissions(self):
        """
        Define los permisos según la acción.
        
        Lógica:
        - create: Solo médicos
        - validate: Solo administradores
        - list: Autenticado (validación ownership en método)
        
        Returns:
            list: Lista de instancias de permisos
        """
        if self.action == 'create':
            # Solo médicos suben documentos
            return [IsMedico()]
        
        elif self.action == 'validate':
            # Solo administradores validan
            return [IsAdministrador()]
        
        else:
            # list: autenticado + validación en método
            return [IsAuthenticated()]
    
    # =========================================================================
    # ENDPOINTS DE LECTURA
    # =========================================================================
    
    def list(self, request):
        """
        GET /api/documentos/?id_usuario_medico=X
        
        Lista los documentos de un médico.
        
        Permiso: 
        - Médico puede ver solo sus propios documentos
        - Admin puede ver documentos de cualquier médico
        
        Query Params:
            id_usuario_medico: ID del médico cuyos documentos se consultan
        
        Response:
            200: Lista de documentos
            400: Falta parámetro id_usuario_medico
            403: No tiene permiso para ver estos documentos
            404: Usuario no es médico
        """
        id_usuario_medico = request.query_params.get("id_usuario_medico")
        
        if not id_usuario_medico:
            return Response(
                {"detail": "Se requiere el parámetro 'id_usuario_medico' en la URL."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        id_usuario_medico = int(id_usuario_medico)
        
        # VALIDACIÓN DE OWNERSHIP: Médico solo ve sus documentos
        if request.user.rol == 'Medico':
            from medicos.models import Medico
            try:
                medico = Medico.objects.get(id_usuario=request.user.id_usuario)
                
                # Verificar que esté consultando sus propios documentos
                if medico.id_usuario != id_usuario_medico:
                    return Response(
                        {
                            "detail": "No tienes permiso para ver los documentos de otros médicos.",
                            "hint": "Solo puedes ver tus propios documentos."
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Medico.DoesNotExist:
                return Response(
                    {"detail": "No estás registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Admin puede ver documentos de cualquier médico
        try:
            docs = sp_documento_list_by_usuario(id_usuario_medico)
            
        except DatabaseError as e:
            msg = str(e).lower()
            
            if "no está registrado como médico" in msg:
                return Response(
                    {"detail": "El usuario no está registrado como médico."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mapear resultados a formato estándar
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
        serializer.is_valid(raise_exception=False)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # =========================================================================
    # ENDPOINTS DE ESCRITURA
    # =========================================================================
    
    def create(self, request):
        """
        POST /api/documentos/
        
        Sube un nuevo documento para validación.
        
        Permiso: Solo Médicos
        
        Validaciones:
        - Médico solo puede subir documentos para sí mismo
        - Médico debe estar activo
        - El tipo de documento debe existir
        
        Request Body:
            {
                "id_usuario_medico": 2,
                "id_tipo_documento": 1,
                "archivo": "documento.pdf"
            }
        
        Response:
            201: Documento subido (estado: Pendiente)
            403: No es el médico correcto o está desactivado
            404: Usuario no es médico o tipo no existe
        """
        # Log para depuración
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Datos recibidos en create: {request.data}")
        logger.info(f"Usuario autenticado: {request.user}")
        
        serializer = DocumentoUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "detail": "Datos inválidos",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        id_usuario_medico = serializer.validated_data["id_usuario_medico"]
        id_tipo_documento = serializer.validated_data["id_tipo_documento"]
        archivo = serializer.validated_data["archivo"]
        
        # VALIDACIÓN DE OWNERSHIP: Médico solo sube sus documentos
        from medicos.models import Medico
        try:
            medico = Medico.objects.get(id_usuario=request.user.id_usuario)
            
            # Verificar que esté subiendo documentos para sí mismo
            if medico.id_usuario != id_usuario_medico:
                return Response(
                    {
                        "detail": "Solo puedes subir documentos para ti mismo.",
                        "hint": f"Tu ID de usuario médico es {medico.id_usuario}"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except Medico.DoesNotExist:
            return Response(
                {"detail": "No estás registrado como médico."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Subir documento mediante stored procedure
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
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if "está desactivado" in msg and "médico" in msg:
                return Response(
                    {
                        "detail": "Tu cuenta de médico está desactivada.",
                        "hint": "No puedes subir documentos hasta que sea reactivada."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "tipo de documento no existe" in msg:
                return Response(
                    {"detail": "El tipo de documento no existe."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "id_documento": nuevo_id,
                "detail": "Documento subido correctamente.",
                "estado": "Pendiente",
                "hint": "Un administrador revisará tu documento pronto."
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], url_path='validar')
    def validate(self, request, pk=None):
        """
        POST /api/documentos/:id/validar/
        
        Valida (aprueba o rechaza) un documento de médico.
        
        Permiso: Solo Administradores
        
        Args:
            pk: ID del documento a validar
        
        Request Body:
            {
                "id_usuario_admin": 3,
                "estado": "Aprobado",  // O "Rechazado"
                "observaciones": "Documento válido"
            }
        
        Response:
            200: Documento validado
            403: No es administrador
            404: Documento no encontrado
        """
        serializer = DocumentoValidacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        estado = serializer.validated_data["estado"]
        observaciones = serializer.validated_data["observaciones"]
        id_usuario_admin = serializer.validated_data["id_usuario_admin"]
        
        # VALIDACIÓN DE OWNERSHIP: Admin usa su propio ID
        from administrador.models import Administrador
        try:
            admin = Administrador.objects.get(id_usuario=request.user.id_usuario)
            
            # Verificar que esté usando su propio ID
            if admin.id_usuario != id_usuario_admin:
                return Response(
                    {
                        "detail": "Solo puedes validar usando tu propio ID de administrador.",
                        "hint": f"Tu ID de usuario administrador es {admin.id_usuario}"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except Administrador.DoesNotExist:
            return Response(
                {"detail": "No estás registrado como administrador."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Validar documento mediante stored procedure
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
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if "documento no existe" in msg:
                return Response(
                    {"detail": "El documento no existe."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not resultado:
            return Response(
                {"detail": "No se pudo obtener el resultado de la validación."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(
            {
                **resultado,
                "detail": f"Documento {estado.lower()} correctamente."
            },
            status=status.HTTP_200_OK
        )


# =============================================================================
# NOTAS PARA EL DESARROLLADOR
# =============================================================================
#
# 1. PERMISOS IMPLEMENTADOS:
#    - list: IsAuthenticated + ownership (médico solo sus docs)
#    - create: IsMedico + ownership (solo sus docs)
#    - validate: IsAdministrador + ownership (usa su ID)
#
# 2. VALIDACIÓN DE OWNERSHIP:
#    - Médico: Solo ve/sube sus propios documentos
#    - Admin: Valida documentos de cualquier médico
#
# 3. FLUJO DE VALIDACIÓN:
#    a) Médico sube documento → Estado: Pendiente
#    b) Admin revisa y valida → Estado: Aprobado/Rechazado
#    c) Médico puede ver estado de sus documentos
#    d) Cuando todos los docs requeridos están aprobados → Médico puede atender
#
# 4. TIPOS DE DOCUMENTOS:
#    - Los tipos se gestionan en tp_documentos
#    - Ejemplos: Título profesional, Licencia médica, Certificado especialidad
#
# 5. STORED PROCEDURES:
#    - sp_documento_upload: Crea documento en estado Pendiente
#    - sp_documento_validate: Cambia estado y registra quien validó
#    - sp_documento_list_by_usuario: Lista docs de un médico
#
# =============================================================================