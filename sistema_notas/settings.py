import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'default-secret-key-for-development')

DEBUG = True  # ⚠️ No olvides ponerlo en False en producción

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'white-glacier-076b9b40f.6.azurestaticapps.net', 'backacademico-gwatdzagd5g8dcbb.eastus-01.azurewebsites.net']  # Agrega tus dominios en producción aquí

# Aplicaciones instaladas
INSTALLED_APPS = [
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'academico',  # Tu app personalizada
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sistema_notas.urls'

# Plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'sistema_notas.wsgi.application'

# Configuración de la base de datos (PostgreSQL en Render)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'academico_base'),  # Nombre de la base de datos
        'USER': os.environ.get('DB_USER', 'academico_base_user'),  # Usuario de la base de datos
        'PASSWORD': os.environ.get('DB_PASSWORD', 'qaLGA2od4wOzOZMT49Cikby8jgLofHGg'),  # Contraseña de la base de datos
        'HOST': os.environ.get('DB_HOST', 'dpg-d0t0uoqdbo4c739o6330-a.oregon-postgres.render.com'),  # Host de la base de datos
        'PORT': '5432',  # Puerto de PostgreSQL
    }
}

# Configuración de caché
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Configuración de logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django-debug.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        }
    }
}

# Validadores de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Para producción con collectstatic

# Configuración de modelos personalizados
AUTH_USER_MODEL = 'academico.User'

# Login y Logout
LOGIN_URL = '/academico/login/'
LOGIN_REDIRECT_URL = '/academico/lista_calificaciones/'
LOGOUT_REDIRECT_URL = '/academico/login/'

# Configuración de la sesión
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1800  # 30 minutos
SESSION_SAVE_EVERY_REQUEST = True

# Clave para evitar los warnings por claves primarias automáticas
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Variables de entorno para la base de datos
DB_NAME = os.getenv('DB_NAME', 'academico_base')
DB_USER = os.getenv('DB_USER', 'academico_base_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'qaLGA2od4wOzOZMT49Cikby8jgLofHGg')
DB_HOST = os.getenv('DB_HOST', 'dpg-d0t0uoqdbo4c739o6330-a.oregon-postgres.render.com')

def test_settings_configuration(settings):
    assert settings.AUTH_USER_MODEL == 'academico.User'
    assert settings.LANGUAGE_CODE == 'es-es'
    assert settings.TIME_ZONE == 'America/Bogota'
    assert settings.SESSION_COOKIE_AGE == 1800
