from django.db import connection, DatabaseError


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ------------------------------
# Obtener médico por ID_Usuario
# ------------------------------
def sp_medico_get_by_usuario(id_usuario):
    with connection.cursor() as cursor:
        cursor.callproc("sp_medico_get_by_usuario", [id_usuario])
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id_medico": row[0],
            "id_usuario": row[1],
            "nombre": row[2],
            "apellidos": row[3],
            "documento": row[4],
            "correo": row[5],
            "telefono": row[6],
            "licencia": row[7],
            "anios_experiencia": row[8],
            "descripcion_perfil": row[9],
            "foto": row[10],
            "email": row[11],
            "vereda": row[12],
            "estado_validacion": row[13],
            "activo": bool(row[14]),
        }


# ------------------------------
# Listado general
# ------------------------------
def sp_medico_list():
    with connection.cursor() as cursor:
        cursor.callproc("sp_medico_list")
        return dictfetchall(cursor)


# ------------------------------
# Listar por estado (Pendiente/Aprobado/Rechazado)
# ------------------------------
def sp_medico_list_by_estado(estado):
    with connection.cursor() as cursor:
        cursor.callproc("sp_medico_list_by_estado", [estado])
        return dictfetchall(cursor)


# ------------------------------
# Actualizar médico
# ------------------------------
def sp_medico_update(id_usuario, **kwargs):
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_medico_update", [
                id_usuario,
                kwargs["licencia"],
                kwargs["anios_experiencia"],
                kwargs["descripcion_perfil"],
                kwargs["foto"],
                kwargs["email"],
                kwargs["vereda"],
            ])
            row = cursor.fetchone()
            return row[0] if row else 0
        except DatabaseError as e:
            raise e


# ------------------------------
# Estado de validación del médico
# ------------------------------
def sp_medico_estado(id_usuario):
    with connection.cursor() as cursor:
        cursor.callproc("sp_medico_estado", [id_usuario])
        row = cursor.fetchone()
        if not row:
            return None

        return {
            "id_medico": row[0],
            "id_usuario": row[1],
            "nombre": row[2],
            "apellidos": row[3],
            "usuario_activo": bool(row[4]),
            "estado_validacion": row[5],
            "total_tipos_documento": row[6],
            "total_tipos_subidos": row[7],
            "total_aprobados": row[8],
            "total_pendientes": row[9],
            "total_rechazados": row[10],
        }
