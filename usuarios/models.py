"""
Modelo Usuario - Salud Rural

Modelo base para todos los usuarios del sistema.
Representa la tabla 'usuario' en la base de datos.

IMPORTANTE:
- managed = False: Django NO gestiona esta tabla (la gestiona MySQL con SPs)
- La tabla debe existir en la BD antes de usar este modelo
- Los métodos agregados NO modifican la tabla, solo interactúan con ella
"""

from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Usuario(models.Model):
    """
    Modelo de Usuario base.
    
    Este modelo representa a todos los usuarios del sistema, independientemente
    de su rol (Paciente, Medico, Administrador).
    
    Relaciones:
    - Un Usuario puede tener un Paciente (1:1)
    - Un Usuario puede tener un Medico (1:1)
    - Un Usuario puede tener un Administrador (1:1)
    
    El rol se determina por el campo 'rol' y las tablas relacionadas.
    """
    
    # Campos de la tabla (mapeo exacto a la BD)
    id_usuario = models.AutoField(db_column='ID_Usuario', primary_key=True)
    nombre = models.CharField(db_column='Nombre', max_length=100, null=True)
    apellidos = models.CharField(db_column='Apellidos', max_length=100, null=True)
    documento = models.CharField(db_column='Documento', max_length=50, null=True)
    fecha_nacimiento = models.DateField(db_column='FechaNacimiento', null=True)
    correo = models.CharField(db_column='Correo', max_length=100, null=True)
    telefono = models.CharField(db_column='Telefono', max_length=20, null=True)
    
    # Contraseña: almacena el hash, no el texto plano
    # Formato: pbkdf2_sha256$iterations$salt$hash
    contrasena = models.CharField(db_column='Contrasena', max_length=255, null=True)
    
    # Rol define el tipo de usuario
    rol = models.CharField(db_column='Rol', max_length=20)
    
    # Soft delete: usuarios no se eliminan, se desactivan
    activo = models.BooleanField(db_column='Activo', default=True)
    motivo_inactivacion = models.CharField(db_column='MotivoInactivacion', max_length=200, null=True)
    fecha_inactivacion = models.DateTimeField(db_column='FechaInactivacion', null=True)

    class Meta:
        # managed = False: Django NO crea/modifica/elimina esta tabla
        # La tabla es gestionada por MySQL y los Stored Procedures
        managed = False
        db_table = 'usuario'
    
    # =========================================================================
    # CONFIGURACIÓN PARA AUTENTICACIÓN DE DJANGO
    # =========================================================================
    
    # Campo usado como username (para login)
    USERNAME_FIELD = 'correo'
    
    # Campos requeridos además del USERNAME_FIELD
    REQUIRED_FIELDS = ['nombre', 'apellidos', 'documento']

    def __str__(self):
        """Representación en string del usuario."""
        return f"{self.nombre} {self.apellidos} ({self.rol})"
    
    # =========================================================================
    # MÉTODOS REQUERIDOS POR DJANGO AUTH
    # =========================================================================
    
    @property
    def pk(self):
        """
        Primary key para compatibilidad con Django.
        Django espera 'pk', pero nuestro campo se llama 'id_usuario'.
        """
        return self.id_usuario
    
    def get_username(self):
        """
        Retorna el username (correo en nuestro caso).
        Requerido por Django auth system.
        """
        return self.correo
    
    def get_full_name(self):
        """
        Retorna el nombre completo del usuario.
        Requerido por Django auth system.
        """
        return f"{self.nombre} {self.apellidos}".strip()
    
    def get_short_name(self):
        """
        Retorna el nombre corto del usuario.
        Requerido por Django auth system.
        """
        return self.nombre
    
    @property
    def is_active(self):
        """
        Compatibilidad con Django: mapea 'activo' a 'is_active'.
        """
        return self.activo
    
    @property
    def is_staff(self):
        """
        Define si el usuario puede acceder al admin de Django.
        Solo administradores pueden acceder.
        """
        return self.rol == 'Administrador'
    
    @property
    def is_superuser(self):
        """
        Define si el usuario tiene todos los permisos.
        Solo administradores.
        """
        return self.rol == 'Administrador'
    
    def has_perm(self, perm, obj=None):
        """
        Verifica si el usuario tiene un permiso específico.
        Administradores tienen todos los permisos.
        """
        return self.rol == 'Administrador'
    
    def has_perms(self, perm_list, obj=None):
        """
        Verifica si el usuario tiene una lista de permisos.
        """
        return self.rol == 'Administrador'
    
    def has_module_perms(self, app_label):
        """
        Verifica si el usuario tiene permisos para un módulo.
        """
        return self.rol == 'Administrador'
    
    # =========================================================================
    # MÉTODOS DE AUTENTICACIÓN (NUEVOS)
    # =========================================================================
    
    def set_password(self, raw_password):
        """
        Hashea una contraseña en texto plano y la asigna al usuario.
        
        Usa el sistema de hasheo de Django (PBKDF2 con SHA256 por defecto).
        Es seguro, lento (intencional para prevenir brute force), y estándar.
        
        Args:
            raw_password (str): Contraseña en texto plano
            
        Returns:
            None: Modifica el campo self.contrasena
            
        Ejemplo:
            usuario = Usuario.objects.get(id_usuario=1)
            usuario.set_password('nueva_password')
            usuario.save(update_fields=['contrasena'])
            
        Nota:
            Este método NO guarda en BD automáticamente.
            Debes llamar a .save() después.
        """
        self.contrasena = make_password(raw_password)
    
    def check_password(self, raw_password):
        """
        Verifica si una contraseña en texto plano coincide con el hash almacenado.
        
        Usa comparación de tiempo constante para prevenir timing attacks.
        
        Args:
            raw_password (str): Contraseña en texto plano a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False si no
            
        Ejemplo:
            usuario = Usuario.objects.get(correo='user@example.com')
            if usuario.check_password('password123'):
                print('Login exitoso')
            else:
                print('Contraseña incorrecta')
        """
        # check_password maneja el caso de contrasena=None
        return check_password(raw_password, self.contrasena)
    
    # =========================================================================
    # PROPIEDADES DE CONVENIENCIA
    # =========================================================================
    
    @property
    def is_authenticated(self):
        """
        Propiedad requerida por Django para compatibilidad con auth system.
        
        Returns:
            bool: Siempre True para usuarios en BD
        """
        return True
    
    @property
    def is_anonymous(self):
        """
        Propiedad requerida por Django para compatibilidad con auth system.
        
        Returns:
            bool: Siempre False para usuarios autenticados
        """
        return False
    
    @property
    def is_paciente(self):
        """
        Verifica si el usuario es un paciente.
        
        Returns:
            bool: True si rol='Paciente'
        """
        return self.rol == 'Paciente'
    
    @property
    def is_medico(self):
        """
        Verifica si el usuario es un médico.
        
        Returns:
            bool: True si rol='Medico'
        """
        return self.rol == 'Medico'
    
    @property
    def is_administrador(self):
        """
        Verifica si el usuario es un administrador.
        
        Returns:
            bool: True si rol='Administrador'
        """
        return self.rol == 'Administrador'
    
    @property
    def nombre_completo(self):
        """
        Retorna el nombre completo del usuario.
        
        Returns:
            str: Nombre y apellidos concatenados
        """
        return f"{self.nombre} {self.apellidos}".strip()


# =============================================================================
# NOTAS SOBRE SEGURIDAD DE CONTRASEÑAS
# =============================================================================
#
# 1. ALGORITMO DE HASH:
#    Django usa PBKDF2 con SHA256 por defecto:
#    - 260,000 iteraciones (Django 4.0+)
#    - Salt aleatorio único por contraseña
#    - Resistente a rainbow tables y brute force
#
# 2. FORMATO DEL HASH:
#    pbkdf2_sha256$260000$salt$hash
#    - pbkdf2_sha256: Algoritmo usado
#    - 260000: Número de iteraciones
#    - salt: Salt aleatorio (base64)
#    - hash: Hash resultante (base64)
#
# 3. MIGRACIÓN DE CONTRASEÑAS EXISTENTES:
#    Si la BD tiene contraseñas en texto plano:
#    - Ejecutar script de migración (hash_passwords.py)
#    - Hashear todas las contraseñas existentes
#    - Esto es un proceso ONE-TIME
#
# 4. ALTERNATIVAS DE HASH:
#    Django soporta múltiples algoritmos:
#    - argon2 (más seguro, requiere librería)
#    - bcrypt (popular, requiere librería)
#    - scrypt (moderno, requiere librería)
#    
#    Para cambiar, agregar en settings.py:
#    PASSWORD_HASHERS = [
#        'django.contrib.auth.hashers.Argon2PasswordHasher',
#        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
#    ]
#
# =============================================================================