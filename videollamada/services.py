from django.db import connection, DatabaseError


def sp_videollamada_crear(id_cita, enlace):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_videollamada_crear", [
                id_cita,
                enlace
            ])
            row = cursor.fetchone()
            return row[0] if row else "Videollamada configurada"
        except DatabaseError as e:
            raise e


def sp_videollamada_get(id_cita):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_videollamada_get", [id_cita])

            row = cursor.fetchone()
            if not row:
                return None

            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))

        except DatabaseError as e:
            raise e
