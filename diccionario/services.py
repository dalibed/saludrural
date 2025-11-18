from django.db import connection, OperationalError, DatabaseError


def sp_diccionario_create(id_usuario_admin, termino, definicion, causas, tratamientos):
    with connection.cursor() as cursor:
        cursor.callproc('sp_diccionario_create', [
            id_usuario_admin,
            termino,
            definicion,
            causas,
            tratamientos,
        ])
        row = cursor.fetchone()
        return int(row[0]) if row else None


def sp_diccionario_update(id_usuario_admin, id_termino, termino, definicion, causas, tratamientos):
    with connection.cursor() as cursor:
        cursor.callproc('sp_diccionario_update', [
            id_usuario_admin,
            id_termino,
            termino,
            definicion,
            causas,
            tratamientos
        ])
        row = cursor.fetchone()
        return int(row[0]) if row else 0


def sp_diccionario_delete(id_usuario_admin, id_termino):
    with connection.cursor() as cursor:
        cursor.callproc('sp_diccionario_delete', [
            id_usuario_admin,
            id_termino
        ])
        row = cursor.fetchone()
        return int(row[0]) if row else 0


def sp_diccionario_get(id_termino):
    with connection.cursor() as cursor:
        cursor.callproc('sp_diccionario_get', [id_termino])
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id_termino": row[0],
            "termino": row[1],
            "definicion": row[2],
            "causas": row[3],
            "tratamientos": row[4],
        }


def sp_diccionario_list():
    with connection.cursor() as cursor:
        cursor.callproc('sp_diccionario_list')
        rows = cursor.fetchall()

        return [
            {
                "id_termino": r[0],
                "termino": r[1],
                "definicion": r[2],
                "causas": r[3],
                "tratamientos": r[4],
            }
            for r in rows
        ]


def sp_diccionario_search(busqueda):
    with connection.cursor() as cursor:
        cursor.callproc('sp_diccionario_search', [busqueda])
        rows = cursor.fetchall()

        return [
            {
                "id_termino": r[0],
                "termino": r[1],
                "definicion": r[2],
                "causas": r[3],
                "tratamientos": r[4],
            }
            for r in rows
        ]
