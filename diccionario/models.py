from django.db import models

class DiccionarioMedico(models.Model):
    id_termino = models.AutoField(db_column='ID_Termino', primary_key=True)
    termino = models.CharField(db_column='Termino', max_length=100)
    definicion = models.TextField(db_column='Definicion')
    causas = models.TextField(db_column='Causas')
    tratamientos = models.TextField(db_column='Tratamientos')

    class Meta:
        managed = False
        db_table = 'Diccionario_Medico'
