from django.db import models


class HistoriaEntrada(models.Model):
    id_entrada = models.AutoField(db_column='ID_Entrada', primary_key=True)
    id_historia = models.IntegerField(db_column='ID_Historia', null=True)
    id_cita = models.IntegerField(db_column='ID_Cita', null=True)
    diagnostico = models.TextField(db_column='Diagnostico', null=True)
    tratamiento = models.TextField(db_column='Tratamiento', null=True)
    notas = models.TextField(db_column='Notas', null=True)
    fecha_registro = models.DateTimeField(db_column='FechaRegistro', null=True)

    class Meta:
        managed = False
        db_table = 'historia_entrada'
