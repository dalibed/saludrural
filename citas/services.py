from django.db import connection, DatabaseError


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def sp_cita_create(id_usuario_paciente, id_usuario_medico, id_agenda, motivo):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_cita_create", [
                id_usuario_paciente,
                id_usuario_medico,
                id_agenda,
                motivo
            ])
            row = cursor.fetchone()
            return row[0]
        except DatabaseError as e:
            raise e


def sp_cita_cancelar(id_cita, id_usuario, motivo):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_cita_cancelar", [
                id_cita,
                id_usuario,
                motivo
            ])
            row = cursor.fetchone()
            return row[0] if row else 0
        except DatabaseError as e:
            raise e


def sp_cita_list_paciente(id_usuario_paciente):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_cita_list_paciente", [id_usuario_paciente])
            return dictfetchall(cursor)
        except DatabaseError as e:
            raise e


def sp_cita_list_medico(id_usuario_medico):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_cita_list_medico", [id_usuario_medico])
            return dictfetchall(cursor)
        except DatabaseError as e:
            raise e
from django.db import connection, DatabaseError

def sp_cita_completar(id_usuario_medico, id_cita):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_cita_completar", [
                id_usuario_medico,
                id_cita
            ])
            row = cursor.fetchone()
            return row[0] if row else "Cita completada"
        except DatabaseError as e:
            raise e


def sp_cita_aceptar(id_usuario_medico, id_cita):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_cita_aceptar", [
                id_usuario_medico,
                id_cita
            ])
            row = cursor.fetchone()
            return row[0] if row else "Cita aceptada correctamente"
        except DatabaseError as e:
            raise e
