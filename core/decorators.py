from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def student_required(function):
    """
    Decorador que verifica si el usuario es un estudiante.
    Redirige a login si no está autenticado o muestra error si no tiene el rol adecuado.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        if user.role != 'student':
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrap

def teacher_required(function):
    """
    Decorador que verifica si el usuario es un profesor.
    Redirige a login si no está autenticado o muestra error si no tiene el rol adecuado.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        if user.role != 'teacher':
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrap

def admin_required(function):
    """
    Decorador que verifica si el usuario es un administrador.
    Redirige a login si no está autenticado o muestra error si no tiene el rol adecuado.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        if user.role != 'admin':
            messages.error(request, "No tienes permisos para acceder a esta página.")
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrap

# Decorator para vistas basadas en clases
def role_required(allowed_roles):
    """
    Decorador para vistas basadas en clases que verifica si el usuario tiene uno de los roles permitidos.
    
    Ejemplo de uso:
    @method_decorator(role_required(['admin', 'teacher']), name='dispatch')
    class MyView(View):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, "No tienes permisos para acceder a esta página.")
                return redirect('login')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator