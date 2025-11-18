from django.db import connection

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def sp_usuario_create(**kwargs):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_usuario_create", [
                kwargs["nombre"],
                kwargs["apellidos"],
                kwargs["documento"],
                kwargs["fecha_nacimiento"],
                kwargs["correo"],
                kwargs["telefono"],
                kwargs["contrasena"],
                kwargs["rol"],
            ])
            result = cursor.fetchone()
            return result[0]
        except Exception as e:
            raise e


def sp_usuario_update(id_usuario, **kwargs):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_usuario_update", [
                id_usuario,
                kwargs["nombre"],
                kwargs["apellidos"],
                kwargs["correo"],
                kwargs["telefono"],
            ])
            result = cursor.fetchone()
            return result[0]
        except Exception as e:
            raise e


def sp_usuario_get(id_usuario):
    with connection.cursor() as cursor:
        cursor.callproc("sp_usuario_get", [id_usuario])
        row = cursor.fetchone()
        if not row:
            return None

        data = {
            "id_usuario": row[0],
            "nombre": row[1],
            "apellidos": row[2],
            "documento": row[3],
            "correo": row[4],
            "telefono": row[5],
            "rol": row[6],
            "activo": row[7],
            "motivo_inactivacion": row[8],
            "fecha_inactivacion": row[9],
        }
        return data


def sp_usuario_list():
    with connection.cursor() as cursor:
        cursor.callproc("sp_usuario_list")
        return dictfetchall(cursor)


def sp_usuario_deactivate(id_usuario, motivo):
    with connection.cursor() as cursor:
        cursor.callproc("sp_usuario_deactivate", [id_usuario, motivo])
        result = cursor.fetchone()
        return result[0]


def sp_usuario_activate(id_usuario):
    with connection.cursor() as cursor:
        cursor.callproc("sp_usuario_activate", [id_usuario])
        result = cursor.fetchone()
        return result[0]
