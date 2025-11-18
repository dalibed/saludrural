from django.db import connection, DatabaseError


def sp_admin_get_id_by_usuario(id_usuario: int):
    """
    Envuelve el SP sp_admin_get_id_by_usuario.

    Devuelve:
        - ID_Admin (int) si existe
        - None si no hay administrador para ese usuario
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_admin_get_id_by_usuario", [id_usuario])
            row = cursor.fetchone()
            return int(row[0]) if row else None
        except DatabaseError as e:
            # La vista se encarga de convertir esto en respuesta HTTP
            raise e
