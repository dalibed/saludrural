from django.db import models

class Agenda(models.Model):
    id_agenda = models.AutoField(db_column='ID_Agenda', primary_key=True)
    id_medico = models.IntegerField(db_column='ID_Medico')
    fecha = models.DateField(db_column='Fecha')
    hora = models.TimeField(db_column='Hora')
    disponible = models.BooleanField(db_column='Disponible', default=True)

    class Meta:
        managed = False
        db_table = 'Agenda'
