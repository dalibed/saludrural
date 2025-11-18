from django.db import models

class Administrador(models.Model):
    id_admin = models.AutoField(db_column='ID_Admin', primary_key=True)
    id_usuario = models.IntegerField(db_column='ID_Usuario')
    cargo = models.CharField(db_column='Cargo', max_length=50, null=True)
    credenciales = models.CharField(db_column='Credenciales', max_length=100, null=True)

    class Meta:
        managed = False
        db_table = 'administrador'
