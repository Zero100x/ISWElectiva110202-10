"""
Vistas de la aplicación core.

Este archivo contiene las vistas (controladores) que manejan las solicitudes
y devuelven las respuestas apropiadas.

Funcionalidades principales:
1. Autenticación (login, logout)
2. Restablecimiento de contraseña
3. Dashboards específicos por rol de usuario
"""

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .forms import CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import User
from .decorators import student_required, teacher_required, admin_required, role_required

# ======== VISTAS DE AUTENTICACIÓN ========

class CustomLoginView(LoginView):
    """
    Vista personalizada para la página de login.
    
    Esta vista maneja:
    - La autenticación del usuario
    - Redirección basada en el rol del usuario
    - Mensajes de error personalizados
    """
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """
        Determina la URL a la que redirigir después de un inicio de sesión exitoso
        basado en el rol del usuario.
        """
        user = self.request.user
        
        # Verificar el rol del usuario y redirigir según corresponda
        if user.role == User.STUDENT:
            return reverse_lazy('student_dashboard')
        elif user.role == User.TEACHER:
            return reverse_lazy('teacher_dashboard')
        elif user.role == User.ADMIN:
            return reverse_lazy('admin_dashboard')
        
        # Si no tiene un rol específico, redirigir a una página predeterminada
        return reverse_lazy('home')
    
    def form_invalid(self, form):
        """
        Maneja el caso cuando el formulario es inválido.
        Agrega mensajes de error específicos según el tipo de error.
        """
        for error in form.non_field_errors():
            messages.error(self.request, error)
        
        # Verificar si hay campos vacíos y mostrar mensajes específicos
        if 'username' in form.errors:
            messages.error(self.request, form.errors['username'][0])
        
        if 'password' in form.errors:
            messages.error(self.request, form.errors['password'][0])
        
        return super().form_invalid(form)


class CustomPasswordResetView(PasswordResetView):
    """
    Vista para solicitar restablecimiento de contraseña.
    
    Permite a los usuarios solicitar un correo para restablecer su contraseña.
    """
    form_class = CustomPasswordResetForm
    template_name = 'core/password_reset.html'
    email_template_name = 'core/password_reset_email.html'
    subject_template_name = 'core/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        """Procesa el formulario válido y envía el correo"""
        email = form.cleaned_data['email']
        
        if not User.objects.filter(email=email).exists():
            messages.error(self.request, 'No existe una cuenta con este correo electrónico.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Se ha enviado un correo con instrucciones para restablecer tu contraseña.')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Vista para confirmar el restablecimiento de contraseña.
    
    Permite a los usuarios establecer una nueva contraseña usando el enlace
    enviado a su correo electrónico.
    """
    form_class = CustomSetPasswordForm
    template_name = 'core/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        """Procesa el cambio de contraseña exitoso"""
        messages.success(self.request, 'Tu contraseña ha sido restablecida exitosamente.')
        return super().form_valid(form)


# ======== VISTAS DE DASHBOARD ========
@method_decorator(role_required(['student']), name='dispatch')
class StudentDashboardView(TemplateView):
    """
    Dashboard para estudiantes.
    
    Solo accesible para usuarios con rol de estudiante.
    """
    template_name = 'core/dashboard_student.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['section'] = 'dashboard'
        return context


@method_decorator(role_required(['teacher']), name='dispatch')
class TeacherDashboardView(TemplateView):
    """
    Dashboard para profesores.
    
    Solo accesible para usuarios con rol de profesor.
    """
    template_name = 'core/dashboard_teacher.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['section'] = 'dashboard'
        return context


@method_decorator(role_required(['admin']), name='dispatch')
class AdminDashboardView(TemplateView):
    """
    Dashboard para administradores.
    
    Solo accesible para usuarios con rol de administrador.
    """
    template_name = 'core/dashboard_admin.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['section'] = 'dashboard'
        return context


# ======== OTRAS VISTAS ========
def custom_logout(request):
    """
    Cierra la sesión del usuario.
    
    Termina la sesión actual y redirecciona a la página de login.
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    """
    Página principal de la aplicación.
    
    Solo accesible para usuarios autenticados.
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['section'] = 'home'
        return context
