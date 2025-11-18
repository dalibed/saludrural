from django.db import connection, DatabaseError

def sp_especialidad_create(nombre, descripcion):
    with connection.cursor() as cursor:
        cursor.callproc('sp_especialidad_create', [nombre, descripcion])
        row = cursor.fetchone()
        return row[0] if row else None


def sp_especialidad_list():
    with connection.cursor() as cursor:
        cursor.callproc('sp_especialidad_list')
        rows = cursor.fetchall()
        return [
            {
                "id_especialidad": r[0],
                "nombre": r[1],
                "descripcion": r[2]
            } for r in rows
        ]


def sp_medico_especialidad_asignar(id_usuario_medico, id_especialidad):
    with connection.cursor() as cursor:
        cursor.callproc(
            'sp_medico_especialidad_asignar',
            [id_usuario_medico, id_especialidad]
        )
        row = cursor.fetchone()
        return int(row[0]) if row else 0


def sp_medico_especialidad_list(id_usuario_medico):
    with connection.cursor() as cursor:
        cursor.callproc('sp_medico_especialidad_list', [id_usuario_medico])
        rows = cursor.fetchall()
        return [
            {
                "id_especialidad": r[0],
                "nombre": r[1],
                "descripcion": r[2]
            } for r in rows
        ]
