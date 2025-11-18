from django.db import connection, DatabaseError


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Crear rango de agenda
def sp_agenda_create_range(id_usuario_medico, fecha, hora_inicio, hora_fin):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_agenda_create_range", [
                id_usuario_medico,
                fecha,
                hora_inicio,
                hora_fin
            ])
            row = cursor.fetchone()
            return row[0] if row else 0
        except DatabaseError as e:
            raise e


# Activar/desactivar un slot
def sp_agenda_toggle_slot(id_usuario_medico, id_agenda, disponible):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_agenda_toggle_slot", [
                id_usuario_medico,
                id_agenda,
                disponible
            ])
            row = cursor.fetchone()
            return row[0] if row else 0
        except DatabaseError as e:
            raise e


# Listado completo de agenda
def sp_agenda_list_by_usuario(id_usuario_medico):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_agenda_list_by_usuario", [id_usuario_medico])
            return dictfetchall(cursor)
        except DatabaseError as e:
            raise e


# Listado de solo slots disponibles
def sp_agenda_list_disponible_by_usuario(id_usuario_medico):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_agenda_list_disponible_by_usuario", [id_usuario_medico])
            return dictfetchall(cursor)
        except DatabaseError as e:
            raise e
