from django.db import models


class Documento(models.Model):
    id_documento = models.AutoField(db_column='ID_Documento', primary_key=True)
    archivo = models.CharField(db_column='Archivo', max_length=200, null=True)
    fecha_subida = models.DateField(db_column='FechaSubida', null=True)
    id_medico = models.IntegerField(db_column='ID_Medico', null=True)
    id_tipo_documento = models.IntegerField(db_column='ID_TipoDocumento', null=True)
    estado = models.CharField(db_column='Estado', max_length=20)

    class Meta:
        managed = False
        db_table = 'documento'


class TipoDocumento(models.Model):
    id_tipo_documento = models.AutoField(db_column='ID_TipoDocumento', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=50, null=True)
    descripcion = models.TextField(db_column='Descripcion', null=True)

    class Meta:
        managed = False
        db_table = 'tipo_documento'


class ValidacionDocumento(models.Model):
    id_validacion = models.AutoField(db_column='ID_Validacion', primary_key=True)
    estado = models.CharField(db_column='Estado', max_length=20, null=True)
    observaciones = models.TextField(db_column='Observaciones', null=True)
    fecha_validacion = models.DateField(db_column='FechaValidacion', null=True)
    id_documento = models.IntegerField(db_column='ID_Documento', null=True)
    id_admin = models.IntegerField(db_column='ID_Admin', null=True)

    class Meta:
        managed = False
        db_table = 'validacion_documento'
