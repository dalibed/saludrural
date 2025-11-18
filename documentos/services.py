from django.db import connection, DatabaseError


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def sp_documento_upload(id_usuario_medico: int, id_tipo_documento: int, archivo: str) -> int:
    """
    Ejecuta sp_documento_upload y retorna el ID del documento creado.
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_documento_upload", [
                id_usuario_medico,
                id_tipo_documento,
                archivo
            ])
            row = cursor.fetchone()
            return int(row[0]) if row else None
        except DatabaseError as e:
            # Se maneja en la vista
            raise e


def sp_documento_validate(id_documento: int, estado: str, observaciones: str, id_usuario_admin: int):
    """
    Ejecuta sp_documento_validate y retorna el resumen del estado del médico y documentos.
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_documento_validate", [
                id_documento,
                estado,
                observaciones,
                id_usuario_admin
            ])
            row = cursor.fetchone()
            if not row:
                return None

            return {
                "estado_medico": row[0],
                "tipos_aprobados": row[1],
                "tipos_requeridos": row[2],
                "mensaje": row[3],
            }
        except DatabaseError as e:
            raise e


def sp_documento_list_by_usuario(id_usuario_medico: int):
    """
    Ejecuta sp_documento_list_by_usuario y retorna lista de documentos del médico.
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_documento_list_by_usuario", [id_usuario_medico])
            return dictfetchall(cursor)
        except DatabaseError as e:
            raise e
