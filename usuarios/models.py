from django.db import models

class Usuario(models.Model):
    id_usuario = models.AutoField(db_column='ID_Usuario', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=100, null=True)
    apellidos = models.CharField(db_column='Apellidos', max_length=100, null=True)
    documento = models.CharField(db_column='Documento', max_length=50, null=True)
    fecha_nacimiento = models.DateField(db_column='FechaNacimiento', null=True)
    correo = models.CharField(db_column='Correo', max_length=100, null=True)
    telefono = models.CharField(db_column='Telefono', max_length=20, null=True)
    contrasena = models.CharField(db_column='Contrasena', max_length=100, null=True)
    rol = models.CharField(db_column='Rol', max_length=20)
    activo = models.BooleanField(db_column='Activo', default=True)
    motivo_inactivacion = models.CharField(db_column='MotivoInactivacion', max_length=200, null=True)
    fecha_inactivacion = models.DateTimeField(db_column='FechaInactivacion', null=True)

    class Meta:
        managed = False
        db_table = 'usuario'

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
