from django.db import connection, DatabaseError


def sp_notificacion_list_paciente(id_usuario_paciente: int):
    with connection.cursor() as cursor:
        cursor.callproc('sp_notificacion_list_paciente', [id_usuario_paciente])
        rows = cursor.fetchall()
        return [
            {
                "id_notificacion": r[0],
                "tipo": r[1],
                "mensaje": r[2],
                "fecha_envio": r[3],
                "id_cita": r[4],
                "fecha_cita": r[5],
                "hora_cita": r[6],
            }
            for r in rows
        ]


def sp_notificacion_list_medico(id_usuario_medico: int):
    with connection.cursor() as cursor:
        cursor.callproc('sp_notificacion_list_medico', [id_usuario_medico])
        rows = cursor.fetchall()
        return [
            {
                "id_notificacion": r[0],
                "tipo": r[1],
                "mensaje": r[2],
                "fecha_envio": r[3],
                "id_cita": r[4],
                "fecha_cita": r[5],
                "hora_cita": r[6],
            }
            for r in rows
        ]
