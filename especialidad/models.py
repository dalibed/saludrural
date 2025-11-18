from django.db import models

class Especialidad(models.Model):
    id_especialidad = models.AutoField(db_column='ID_Especialidad', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=100)
    descripcion = models.TextField(db_column='Descripcion', null=True)

    class Meta:
        managed = False
        db_table = 'Especialidad'
