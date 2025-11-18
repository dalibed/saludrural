from django.db import models

class Cita(models.Model):
    id_cita = models.AutoField(db_column='ID_Cita', primary_key=True)
    estado = models.CharField(db_column='Estado', max_length=20)
    id_paciente = models.IntegerField(db_column='ID_Paciente')
    id_medico = models.IntegerField(db_column='ID_Medico')
    id_agenda = models.IntegerField(db_column='ID_Agenda')
    motivo_consulta = models.TextField(db_column='MotivoConsulta', null=True)

    class Meta:
        managed = False
        db_table = 'cita'
