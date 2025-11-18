from django.db import connection, DatabaseError


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    row = cursor.fetchone()
    if not row:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def sp_historia_entrada_create(id_usuario_medico: int,
                               id_cita: int,
                               diagnostico: str,
                               tratamiento: str,
                               notas: str):
    with connection.cursor() as cursor:
        try:
            cursor.callproc(
                "sp_historia_entrada_create",
                [id_usuario_medico, id_cita, diagnostico, tratamiento, notas]
            )
            row = cursor.fetchone()
            return int(row[0]) if row else None
        except DatabaseError as e:
            raise e


def sp_historia_entrada_update(id_usuario_medico: int,
                               id_entrada: int,
                               diagnostico: str,
                               tratamiento: str,
                               notas: str):
    with connection.cursor() as cursor:
        try:
            cursor.callproc(
                "sp_historia_entrada_update",
                [id_usuario_medico, id_entrada, diagnostico, tratamiento, notas]
            )
            row = cursor.fetchone()
            return int(row[0]) if row else 0
        except DatabaseError as e:
            raise e


def sp_historia_entrada_get(id_entrada: int):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_historia_entrada_get", [id_entrada])
            return dictfetchone(cursor)
        except DatabaseError as e:
            raise e


def sp_historia_entrada_list_by_paciente(id_usuario_paciente: int):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_historia_entrada_list_by_paciente", [id_usuario_paciente])
            return dictfetchall(cursor)
        except DatabaseError as e:
            raise e


def sp_historia_entrada_list_by_medico(id_usuario_medico: int):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_historia_entrada_list_by_medico", [id_usuario_medico])
            return dictfetchall(cursor)
        except DatabaseError as e:
            raise e
