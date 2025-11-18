from django.db import connection, DatabaseError

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def sp_paciente_get_by_usuario(id_usuario):
    with connection.cursor() as cursor:
        cursor.callproc("sp_paciente_get_by_usuario", [id_usuario])
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id_paciente": row[0],
            "id_usuario": row[1],
            "nombre": row[2],
            "apellidos": row[3],
            "documento": row[4],
            "correo": row[5],
            "telefono": row[6],
            "grupo_sanguineo": row[7],
            "seguro_medico": row[8],
            "contacto_emergencia": row[9],
            "telefono_emergencia": row[10],
            "activo": bool(row[11]),
        }


def sp_paciente_list():
    with connection.cursor() as cursor:
        cursor.callproc("sp_paciente_list")
        return dictfetchall(cursor)


def sp_paciente_update(id_usuario, **kwargs):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_paciente_update", [
                id_usuario,
                kwargs["grupo_sanguineo"],
                kwargs["seguro_medico"],
                kwargs["contacto_emergencia"],
                kwargs["telefono_emergencia"]
            ])
            row = cursor.fetchone()
            return row[0] if row else 0
        except DatabaseError as e:
            raise e
