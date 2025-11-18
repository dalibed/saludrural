from django.db import connection, DatabaseError


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    row = cursor.fetchone()
    if not row:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def sp_historia_clinica_get_by_paciente(id_usuario_paciente: int):
    """
    Envuelve sp_historia_clinica_get_by_paciente(IN p_ID_Usuario_Paciente)
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc("sp_historia_clinica_get_by_paciente", [id_usuario_paciente])
            return dictfetchone(cursor)
        except DatabaseError as e:
            raise e


def sp_historia_clinica_update_antecedentes(id_usuario_medico: int,
                                            id_usuario_paciente: int,
                                            antecedentes: str):
    """
    Envuelve sp_historia_clinica_update_antecedentes(
        IN p_ID_Usuario_Medico,
        IN p_ID_Usuario_Paciente,
        IN p_Antecedentes
    )
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc(
                "sp_historia_clinica_update_antecedentes",
                [id_usuario_medico, id_usuario_paciente, antecedentes]
            )
            row = cursor.fetchone()
            return int(row[0]) if row else 0
        except DatabaseError as e:
            raise e


def sp_historia_completa_by_paciente(id_usuario_medico: int, id_usuario_paciente: int):
    """
    Envuelve sp_historia_completa_by_paciente(
        IN p_ID_Usuario_Medico,
        IN p_ID_Usuario_Paciente
    )

    Este SP devuelve 2 resultsets:
    1) Información de historia clínica
    2) Entradas de historia
    """
    with connection.cursor() as cursor:
        try:
            cursor.callproc(
                "sp_historia_completa_by_paciente",
                [id_usuario_medico, id_usuario_paciente]
            )

            # Primer resultset: historia clínica (0 o 1 fila)
            historia_rows = dictfetchall(cursor)
            historia = historia_rows[0] if historia_rows else None

            # Segundo resultset: entradas
            cursor.nextset()
            entradas = dictfetchall(cursor)

            return {
                "historia": historia,
                "entradas": entradas,
            }
        except DatabaseError as e:
            raise e
