"""
Configuración de URLs de la aplicación core.

Este archivo define las rutas URL específicas de la aplicación core,
conectando las URLs con las vistas correspondientes y organizándolas
por categorías funcionales.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    CustomLoginView,
    StudentDashboardView,
    TeacherDashboardView,
    AdminDashboardView,
    HomeView
)

urlpatterns = [
    # === AUTENTICACIÓN ===
    # Página de login personalizada
    path('login/', CustomLoginView.as_view(), name='login'),
    # Cierre de sesión
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # === RESTABLECIMIENTO DE CONTRASEÑA ===
    # Solicitud de restablecimiento
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='core/password_reset.html',
             email_template_name='core/password_reset_email.html',
         ), 
         name='password_reset'),
    # Confirmación de solicitud enviada
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='core/password_reset_done.html'
         ), 
         name='password_reset_done'),
    # Formulario para nueva contraseña
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='core/password_reset_confirm.html',
         ), 
         name='password_reset_confirm'),
    # Confirmación de contraseña restablecida
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='core/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # === DASHBOARDS POR ROL ===
    path('dashboard/student/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # === PÁGINA PRINCIPAL ===
    path('', HomeView.as_view(), name='home'),
]
