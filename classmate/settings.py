"""
Archivo de configuración principal de Django para el proyecto Classmate.

Este archivo contiene todas las configuraciones necesarias para el funcionamiento
del proyecto. Cada sección está documentada para facilitar su comprensión.
"""

import os
from pathlib import Path

# CONFIGURACIÓN BÁSICA
# ------------------------------------------------------------------------------
# BASE_DIR: Directorio raíz del proyecto, usado para construir otras rutas
BASE_DIR = Path(__file__).resolve().parent.parent

# CONFIGURACIÓN DE SEGURIDAD
# ------------------------------------------------------------------------------
# SECURITY WARNING: ¡Mantén la clave secreta en secreto en producción!
SECRET_KEY = 'django-insecure-your-secret-key-here'

# SECURITY WARNING: Desactiva el modo DEBUG en producción
DEBUG = True  # True = modo desarrollo, False = modo producción

# Define qué hosts pueden acceder a tu aplicación
ALLOWED_HOSTS = ['*']  # ['*'] permite todos los hosts (solo para desarrollo)

# APLICACIONES
# ------------------------------------------------------------------------------
# Lista de aplicaciones Django activadas en este proyecto
INSTALLED_APPS = [
    'core.apps.CoreConfig',  # Nuestra app principal (primero para prioridad)
    'django.contrib.admin',  # Panel de administración
    'django.contrib.auth',   # Sistema de autenticación
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # Manejo de archivos estáticos
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# Componentes que procesan las solicitudes/respuestas HTTP
# El orden es importante - no modificar a menos que sepas lo que haces
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CONFIGURACIÓN DE URLS
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'classmate.urls'

# PLANTILLAS
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Busca plantillas en el directorio 'templates' del proyecto
        ],
        'APP_DIRS': True,  # También busca plantillas en el directorio 'templates' de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# CONFIGURACIÓN DE WSGI
# ------------------------------------------------------------------------------
WSGI_APPLICATION = 'classmate.wsgi.application'

# BASE DE DATOS
# ------------------------------------------------------------------------------
# SQLite para desarrollo - simple y no requiere configuración adicional
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# AUTENTICACIÓN
# ------------------------------------------------------------------------------
# Modelo de usuario personalizado
AUTH_USER_MODEL = 'core.User'  # Usa nuestro modelo User personalizado

# URLs para redirección después de login/logout
LOGIN_URL = 'login'  # Nombre de la URL para iniciar sesión
LOGIN_REDIRECT_URL = '/'  # Redirige aquí después de iniciar sesión exitosamente
LOGOUT_REDIRECT_URL = '/login/'  # Redirige aquí después de cerrar sesión

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Longitud mínima de 8 caracteres
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# EMAIL
# ------------------------------------------------------------------------------
# Configuración simplificada de email
if DEBUG:
    # En desarrollo, los emails se muestran en la consola
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Configuración para producción (completar con tus datos reales)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'your-email@gmail.com'
    EMAIL_HOST_PASSWORD = 'your-email-password'

# Configuración adicional de correo
DEFAULT_FROM_EMAIL = 'noreply@classmate.com'
EMAIL_SUBJECT_PREFIX = '[Classmate] '

# ARCHIVOS ESTÁTICOS Y MEDIA
# ------------------------------------------------------------------------------
# Archivos estáticos (CSS, JavaScript, imágenes)
STATIC_URL = '/static/'  # URL para acceder a los archivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Directorio para collectstatic (producción)
STATICFILES_DIRS = [BASE_DIR / 'static']  # Directorios adicionales de estáticos

# Archivos subidos por usuarios
MEDIA_URL = '/media/'  # URL para acceder a los archivos multimedia
MEDIA_ROOT = BASE_DIR / 'media'  # Directorio donde se guardan los archivos

# CONFIGURACIÓN ADICIONAL
# ------------------------------------------------------------------------------
# Zona horaria
TIME_ZONE = 'America/Bogota'  # Ajusta a tu zona horaria
USE_TZ = True  # Usar zonas horarias

# Tipo de campo automático por defecto para modelos
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ID del sitio (necesario para algunas aplicaciones de Django)
SITE_ID = 1
