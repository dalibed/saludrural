"""
Django settings for backend project - Salud Rural

Configuración actualizada con autenticación JWT y permisos.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-cprx@@m46rxv-ojzrq6w0rf_vmu7)#%38)m7ym08v#7u_a%s(e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # Para logout con blacklist
    'corsheaders',
    
    # Local apps
    'autenticacion',  # NUEVO: Sistema de autenticación
    'usuarios',
    'pacientes',
    'medicos',
    'administrador',
    'tp_documentos',
    'documentos',
    'agenda',
    'citas',
    'diccionario',
    'videollamada',
    'especialidad',
    'notificaciones',
    
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
CORS_ALLOW_ALL_ORIGINS = True
ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "saludrural2",
        "USER": "root",
        "PASSWORD": "1908798",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            "autocommit": True,
        },
    }
}


# =============================================================================
# MODELO DE USUARIO PERSONALIZADO
# =============================================================================

# Especificar el modelo de usuario personalizado
# IMPORTANTE: Debe definirse ANTES de las migraciones
AUTH_USER_MODEL = 'usuarios.Usuario'

# Backend de autenticación personalizado
# Permite autenticar con correo en lugar de username
AUTHENTICATION_BACKENDS = [
    'usuarios.auth_backend.UsuarioBackend',  # Nuestro backend personalizado
]


# =============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN JWT
# =============================================================================

# Django REST Framework Configuration
REST_FRAMEWORK = {
    # Autenticación: JWT como método por defecto
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    
    # Permisos: Por defecto NO requiere autenticación
    # Cada view especifica sus propios permisos
    # Esto permite tener endpoints públicos (registro, login) y protegidos
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    
    # Formato de fechas (opcional)
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
}

# Simple JWT Configuration
SIMPLE_JWT = {
    # Duración del access token (60 minutos)
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    
    # Duración del refresh token (1 día)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    
    # Permitir rotar refresh tokens (mayor seguridad)
    'ROTATE_REFRESH_TOKENS': True,
    
    # Agregar tokens antiguos a blacklist cuando se rotan
    'BLACKLIST_AFTER_ROTATION': True,
    
    # Algoritmo de firma de tokens
    'ALGORITHM': 'HS256',
    
    # Clave de firma (usa SECRET_KEY de Django)
    'SIGNING_KEY': SECRET_KEY,
    
    # Campo del modelo Usuario que se usa como identificador
    'USER_ID_FIELD': 'id_usuario',
    
    # Nombre del claim en el JWT que contiene el user_id
    'USER_ID_CLAIM': 'user_id',
    
    # Tipo de token en el header
    'AUTH_HEADER_TYPES': ('Bearer',),
    
    # Modelo de usuario personalizado
    'USER_MODEL': 'usuarios.Usuario',
    
    # Actualizar última vez que se usó el token
    'UPDATE_LAST_LOGIN': True,
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "127.0.0.1:3000",
    "localhost:3000",
]