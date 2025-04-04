from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

class RoleRequiredMixin(AccessMixin):
    """
    Mixin que verifica si el usuario tiene uno de los roles permitidos.
    """
    allowed_roles = []
    permission_denied_message = "No tienes permisos para acceder a esta página."
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.role in self.allowed_roles:
            messages.error(request, self.permission_denied_message)
            return redirect('login')
        
        return super().dispatch(request, *args, **kwargs)

class StudentRequiredMixin(RoleRequiredMixin):
    """
    Mixin que verifica si el usuario es un estudiante.
    """
    allowed_roles = ['student']

class TeacherRequiredMixin(RoleRequiredMixin):
    """
    Mixin que verifica si el usuario es un profesor.
    """
    allowed_roles = ['teacher']

class AdminRequiredMixin(RoleRequiredMixin):
    """
    Mixin que verifica si el usuario es un administrador.
    """
    allowed_roles = ['admin']

class TeacherOrAdminRequiredMixin(RoleRequiredMixin):
    """
    Mixin que verifica si el usuario es un profesor o un administrador.
    """
    allowed_roles = ['teacher', 'admin']