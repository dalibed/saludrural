from django.db import models


class HistoriaClinica(models.Model):
    id_historia = models.AutoField(db_column='ID_Historia', primary_key=True)
    id_paciente = models.IntegerField(db_column='ID_Paciente', null=True)
    antecedentes = models.TextField(db_column='Antecedentes', null=True)
    fecha_creacion = models.DateField(db_column='FechaCreacion', null=True)

    class Meta:
        managed = False
        db_table = 'historia_clinica'
