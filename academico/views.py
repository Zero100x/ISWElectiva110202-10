from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
import json
from .forms import (
    LoginForm,
    RecuperacionUsuarioForm,
    RecuperacionPreguntaForm,
    RecuperacionPasswordForm,
    SecurityConfigForm
)
from .models import User, Calificacion, Asignatura, Periodo, Profesor, Estudiante

# Constantes
MAX_RECOVERY_ATTEMPTS = 3
RECOVERY_TIMEOUT_MINUTES = 30

# ---------- Autenticación ----------
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                
                if user.primer_inicio_sesion:
                    return redirect('configurar_seguridad')
                
                if user.rol == 'estudiante':
                    try:
                        estudiante = Estudiante.objects.get(user=user)
                    except Estudiante.DoesNotExist:
                        # Crear automáticamente el perfil de estudiante si no existe
                        matricula = f"EST{user.id:04d}"  # Genera un número de matrícula basado en el ID del usuario
                        estudiante = Estudiante.objects.create(user=user, matricula=matricula)
                    return redirect('calificaciones_estudiante')
                elif user.rol == 'profesor':
                    try:
                        profesor = Profesor.objects.get(user=user)
                    except Profesor.DoesNotExist:
                        profesor = Profesor.objects.create(user=user)
                    return redirect('lista_calificaciones')
                elif user.rol == 'admin':
                    return redirect('admin:index')
            else:
                messages.error(request, "Tu cuenta está desactivada.")
        else:
            messages.error(request, "Credenciales inválidas")
    return render(request, 'academico/login.html')

@login_required
def logout_view(request):
    logout(request)
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def configurar_seguridad(request):
    if not request.user.primer_inicio_sesion:
        return redirect_to_dashboard(request.user)

    if request.method == 'POST':
        form = SecurityConfigForm(request.POST)
        if form.is_valid():
            user = request.user
            user.pregunta_seguridad = form.cleaned_data['pregunta_seguridad']
            user.respuesta_seguridad = form.cleaned_data['respuesta_seguridad']
            user.primer_inicio_sesion = False
            user.save()
            messages.success(request, "Configuración de seguridad completada.")
            return redirect_to_dashboard(user)
    else:
        form = SecurityConfigForm()

    return render(request, 'academico/configurar_seguridad.html', {'form': form})

def redirect_to_dashboard(user):
    if user.rol == 'profesor':
        return redirect('lista_calificaciones')
    if user.rol == 'estudiante':
        return redirect('calificaciones_estudiante')
    if user.rol == 'admin':
        return redirect('admin:index')
    return redirect('login')

# ---------- Recuperación de Contraseña ----------
def recuperar_contrasena_usuario(request):
    form = RecuperacionUsuarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        try:
            user = User.objects.get(username=username)
            if user.intentos_recuperacion >= MAX_RECOVERY_ATTEMPTS and user.ultimo_intento:
                if timezone.now() < user.ultimo_intento + timedelta(minutes=RECOVERY_TIMEOUT_MINUTES):
                    messages.error(request, "Has superado el número de intentos. Intenta nuevamente en 30 minutos.")
                    return render(request, "academico/recuperar_usuario.html", {"form": form})
                user.intentos_recuperacion = 0
                user.save()

            request.session["recuperar_user"] = user.username
            return redirect("recuperar_contrasena_pregunta")
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")

    return render(request, "academico/recuperar_usuario.html", {"form": form})

def recuperar_contrasena_pregunta(request):
    username = request.session.get("recuperar_user")
    if not username:
        return redirect("recuperar_contrasena_usuario")

    user = get_object_or_404(User, username=username)
    pregunta = user.pregunta_seguridad or "No registrada"
    form = RecuperacionPreguntaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        respuesta = form.cleaned_data["respuesta_seguridad"]
        if respuesta == (user.respuesta_seguridad or ""):
            request.session["recuperacion_permitida"] = True
            return redirect("recuperar_contrasena_reset")
        user.intentos_recuperacion += 1
        user.ultimo_intento = timezone.now()
        user.save()
        messages.error(request, "Respuesta incorrecta.")
        if user.intentos_recuperacion >= MAX_RECOVERY_ATTEMPTS:
            messages.error(request, f"Has superado el número de intentos. Intenta nuevamente en {RECOVERY_TIMEOUT_MINUTES} minutos.")
            return redirect("recuperar_contrasena_usuario")

    return render(request, "academico/recuperar_pregunta.html", {
        "form": form,
        "pregunta": pregunta,
        "username": username,
    })

def recuperar_contrasena_reset(request):
    username = request.session.get("recuperar_user")
    recuperacion_ok = request.session.get("recuperacion_permitida", False)

    if not (username and recuperacion_ok):
        return redirect("recuperar_contrasena_usuario")

    user = get_object_or_404(User, username=username)
    form = RecuperacionPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        password1 = form.cleaned_data["nueva_contrasena"]
        password2 = form.cleaned_data["confirmar_contrasena"]

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif len(password1) < 6:
            messages.error(request, "La contraseña debe tener al menos 6 caracteres.")
        else:
            user.set_password(password1)
            user.intentos_recuperacion = 0
            user.save()
            messages.success(request, "Contraseña actualizada exitosamente. Inicia sesión.")
            request.session.pop("recuperar_user", None)
            request.session.pop("recuperacion_permitida", None)
            return redirect("login")

    return render(request, "academico/recuperar_reset.html", {
        "form": form,
        "username": username,
    })

# ---------- Vistas Académicas ----------
@login_required
def lista_calificaciones(request):
    if request.user.rol != 'profesor':
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('login')

    try:
        profesor = Profesor.objects.get(user=request.user)
    except Profesor.DoesNotExist:
        messages.error(request, "No se encontró el perfil de profesor asociado a tu cuenta.")
        return redirect('login')

    asignaturas = Asignatura.objects.all()
    periodos = Periodo.objects.all()
    asignatura_id = request.GET.get('asignatura')
    periodo_id = request.GET.get('periodo')

    calificaciones = Calificacion.objects.filter(profesor=profesor)
    if asignatura_id:
        calificaciones = calificaciones.filter(asignatura_id=asignatura_id)
    if periodo_id:
        calificaciones = calificaciones.filter(periodo_id=periodo_id)

    mensaje = None if calificaciones.exists() else "No hay datos."
    return render(request, 'academico/lista_calificaciones.html', {
        'calificaciones': calificaciones,
        'asignaturas': asignaturas,
        'periodos': periodos,
        'mensaje': mensaje
    })

@login_required
def calificaciones_estudiante(request):
    if request.user.rol != 'estudiante':
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('login')
        
    try:
        estudiante = Estudiante.objects.get(user=request.user)
        calificaciones = Calificacion.objects.filter(estudiante=estudiante).order_by('periodo', 'asignatura__nombre')
        
        periodos = Periodo.objects.all()
        periodo_actual = request.GET.get('periodo')
        
        if periodo_actual:
            calificaciones = calificaciones.filter(periodo__id=periodo_actual)
            
        return render(request, 'academico/calificaciones_estudiante.html', {
            'calificaciones': calificaciones,
            'periodos': periodos,
            'periodo_actual': periodo_actual
        })
    except Estudiante.DoesNotExist:
        messages.error(request, "No se encontró el perfil de estudiante asociado a tu cuenta.")
        return redirect('login')

@login_required
def editar_calificacion(request, calificacion_id):
    if request.user.rol != 'profesor':
        return JsonResponse({'success': False, 'error': 'No tienes permisos para editar calificaciones'})

    try:
        calificacion = Calificacion.objects.get(id=calificacion_id)

        if calificacion.profesor.user != request.user:
            return JsonResponse({'success': False, 'error': 'No tienes permisos para editar esta calificación'})

        if request.method == 'POST':
            data = json.loads(request.body)

            if 'nota' not in data:
                return JsonResponse({'success': False, 'error': 'La calificación es requerida'})

            try:
                nueva_nota = float(data.get('nota'))
                if not 0 <= nueva_nota <= 5:
                    raise ValueError()

                calificacion.nota = nueva_nota
                calificacion.save()
                return JsonResponse({'success': True})

            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'La calificación debe ser un número entre 0 y 5'
                })

        return JsonResponse({'success': False, 'error': 'Método no permitido'})

    except Calificacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'La calificación no existe'})

    if user is not None and user.rol == 'profesor':
        if not hasattr(user, 'profesor'):
            Profesor.objects.create(user=user)
