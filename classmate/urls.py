"""
Configuración de URLs principal del proyecto Classmate.

Este archivo define las rutas URL principales del proyecto,
incluyendo las rutas administrativas y la inclusión de las URLs
de las aplicaciones del proyecto.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # Incluye todas las URLs de la aplicación core
    # Esto permite mantener las URLs organizadas por aplicación
    path('', include('core.urls')),
]

# Configuración para servir archivos estáticos y multimedia en desarrollo
if settings.DEBUG:
    # Sirve archivos estáticos (CSS, JS, imágenes) en desarrollo
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Sirve archivos multimedia (subidos por usuarios) en desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
