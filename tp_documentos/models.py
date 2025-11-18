from django.db import models

class TipoDocumento(models.Model):
    id_tipo_documento = models.AutoField(db_column='ID_TipoDocumento', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=50)
    descripcion = models.TextField(db_column='Descripcion', null=True)

    class Meta:
        managed = False
        db_table = 'tipo_documento'
