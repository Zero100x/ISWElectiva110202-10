from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('lista_calificaciones/', views.lista_calificaciones, name='lista_calificaciones'),
    
    # Recuperación de contraseña
    path('recuperar-contrasena/', views.recuperar_contrasena_usuario, name='recuperar_contrasena_usuario'),
    path('recuperar-contrasena/pregunta/', views.recuperar_contrasena_pregunta, name='recuperar_contrasena_pregunta'),
    path('recuperar-contrasena/reset/', views.recuperar_contrasena_reset, name='recuperar_contrasena_reset'),
    # Agregar esta nueva ruta
    path('configurar-seguridad/', views.configurar_seguridad, name='configurar_seguridad'),
]