from django.db import connection, DatabaseError


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def sp_tipodoc_create(nombre, descripcion):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_tipodoc_create", [nombre, descripcion])
            row = cursor.fetchone()
            return row[0]
        except DatabaseError as e:
            raise e


def sp_tipodoc_update(pid, nombre, descripcion):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_tipodoc_update", [pid, nombre, descripcion])
            row = cursor.fetchone()
            return row[0]
        except DatabaseError as e:
            raise e


def sp_tipodoc_delete(pid):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_tipodoc_delete", [pid])
            row = cursor.fetchone()
            return row[0]
        except DatabaseError as e:
            raise e


def sp_tipodoc_get(pid):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_tipodoc_get", [pid])
            row = cursor.fetchone()

            if not row:
                return None

            return {
                "id_tipo_documento": row[0],
                "nombre": row[1],
                "descripcion": row[2],
            }

        except DatabaseError as e:
            raise e


def sp_tipodoc_list():
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_tipodoc_list")
            return dictfetchall(cursor)
        except DatabaseError as e:
            raise e
