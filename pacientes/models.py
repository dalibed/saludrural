from django.db import models

class Paciente(models.Model):
    id_paciente = models.AutoField(db_column='ID_Paciente', primary_key=True)
    id_usuario = models.IntegerField(db_column='ID_Usuario', unique=True)
    grupo_sanguineo = models.CharField(db_column='GrupoSanguineo', max_length=5, null=True)
    seguro_medico = models.CharField(db_column='SeguroMedico', max_length=100, null=True)
    contacto_emergencia = models.CharField(db_column='ContactoEmergencia', max_length=100, null=True)
    telefono_emergencia = models.CharField(db_column='TelefonoEmergencia', max_length=20, null=True)

    class Meta:
        managed = False
        db_table = 'paciente'
