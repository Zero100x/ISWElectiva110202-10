from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator  # Añadir esta línea
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db.models import Avg
from .models import Asignatura, Calificacion, User, Periodo, Profesor, Estudiante
from .forms import (
    LoginForm, RecuperacionUsuarioForm, RecuperacionPreguntaForm,
    RecuperacionPasswordForm, SecurityConfigForm, AsignaturaForm, CalificacionForm
)

# Constants
MAX_RECOVERY_ATTEMPTS = 3
RECOVERY_TIMEOUT_MINUTES = 30

# Authentication Views
@never_cache
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            if user.primer_inicio_sesion:
                return redirect('configurar_seguridad')
            return redirect_to_dashboard(user)
        messages.error(request, "Credenciales inválidas o cuenta desactivada.")
    return render(request, 'registration/login.html')

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
            try:
                user = request.user
                user.pregunta_seguridad = form.cleaned_data['pregunta_seguridad']
                user.respuesta_seguridad = form.cleaned_data['respuesta_seguridad']
                user.primer_inicio_sesion = False
                user.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Configuración guardada correctamente',
                    'redirect_url': redirect_to_dashboard(user).url
                })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Error al guardar: {str(e)}'})
        else:
            errores = {campo: errores[0] for campo, errores in form.errors.items()}
            return JsonResponse({
                'status': 'error',
                'message': 'Por favor verifica los datos ingresados',
                'errors': errores
            })
    else:
        form = SecurityConfigForm()
    return render(request, 'academico/configurar_seguridad.html', {'form': form})

def redirect_to_dashboard(user):
    if user.rol == 'profesor':
        return redirect('lista_calificaciones')
    elif user.rol == 'estudiante':
        return redirect('calificaciones_estudiante')
    elif user.rol == 'admin':
        return redirect('informes_rendimiento')
    return redirect('login')

# Password Recovery Views
def recuperar_contrasena_usuario(request):
    form = RecuperacionUsuarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        try:
            user = User.objects.get(username=username)
            if user.intentos_recuperacion >= MAX_RECOVERY_ATTEMPTS and user.ultimo_intento:
                if timezone.now() < user.ultimo_intento + timedelta(minutes=RECOVERY_TIMEOUT_MINUTES):
                    messages.error(request, "Has superado el número de intentos. Intenta nuevamente en 30 minutos.")
                    return render(request, "auth/recuperacion/recuperar_usuario.html", {"form": form})
                user.intentos_recuperacion = 0
                user.save()
            request.session["recuperar_user"] = user.username
            return redirect("recuperar_contrasena_pregunta")
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
    return render(request, "auth/recuperacion/recuperar_usuario.html", {"form": form})

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
    return render(request, "auth/recuperacion/recuperar_pregunta.html", {"form": form, "pregunta": pregunta, "username": username})

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
    return render(request, "auth/recuperacion/recuperar_reset.html", {"form": form, "username": username})

# Academic Views
@login_required
def lista_calificaciones(request):
    if request.user.rol != 'profesor':
        messages.error(request, "Acceso restringido a profesores.")
        return redirect('login')
    try:
        profesor = Profesor.objects.get(user=request.user)
    except Profesor.DoesNotExist:
        messages.error(request, "Perfil de profesor no encontrado.")
        return redirect('login')
    asignatura_id = request.GET.get('asignatura')
    periodo_id = request.GET.get('periodo')
    calificaciones = Calificacion.objects.filter(profesor=profesor).select_related('estudiante__user', 'asignatura', 'periodo')
    if asignatura_id:
        calificaciones = calificaciones.filter(asignatura_id=asignatura_id)
    if periodo_id:
        calificaciones = calificaciones.filter(periodo_id=periodo_id)
    context = {
        'calificaciones': calificaciones,
        'asignaturas': Asignatura.objects.all(),
        'periodos': Periodo.objects.all(),
        'mensaje': "No hay calificaciones registradas." if not calificaciones.exists() else None
    }
    return render(request, 'academico/calificaciones/lista_calificaciones.html', context)

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
        return render(request, 'academico/calificaciones/calificaciones_estudiante.html', {
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
                return JsonResponse({'success': False, 'error': 'La calificación debe ser un número entre 0 y 5'})
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    except Calificacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'La calificación no existe'})

class CrearAsignaturaView(CreateView):
    model = Asignatura
    form_class = AsignaturaForm
    template_name = 'academico/asignaturas/crear_asignatura.html'
    success_url = reverse_lazy('lista_calificaciones')

class CrearCalificacionView(CreateView):
    model = Calificacion
    form_class = CalificacionForm
    template_name = 'academico/calificaciones/crear_calificacion.html'
    success_url = reverse_lazy('lista_calificaciones')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['profesor'] = self.request.user.profesor
        return kwargs

    def form_valid(self, form):
        form.instance.profesor = self.request.user.profesor
        return super().form_valid(form)

def es_profesor(user):
    return user.rol == 'profesor'

@method_decorator([login_required, user_passes_test(es_profesor)], name='dispatch')
class CrearCalificacionView(CreateView):
    model = Calificacion
    form_class = CalificacionForm
    template_name = 'academico/calificaciones/crear_calificacion.html'
    success_url = reverse_lazy('lista_calificaciones')

    def form_valid(self, form):
        form.instance.profesor = Profesor.objects.get(user=self.request.user)
        return super().form_valid(form)
#editar calificaciones
@login_required
@user_passes_test(lambda u: u.rol == 'profesor', login_url='/login/')
def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    if request.method == 'POST':
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            calificacion_editada = form.save(commit=False)
            calificacion_editada.estudiante = calificacion.estudiante
            calificacion_editada.save()
            return redirect('lista_calificaciones')
    else:
        form = CalificacionForm(instance=calificacion)
    return render(request, 'academico/calificaciones/editar_calificacion.html', {'form': form, 'calificacion': calificacion})

#eliminar

@login_required
@user_passes_test(lambda u: u.rol == 'profesor', login_url='/login/')
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    
    # Verificar que el profesor solo puede eliminar sus propias calificaciones
    if calificacion.profesor.user != request.user:
        messages.error(request, "No tienes permiso para eliminar esta calificación.")
        return redirect('lista_calificaciones')
    
    if request.method == 'POST':
        calificacion.delete()
        messages.success(request, "Calificación eliminada correctamente.")
    else:
        messages.error(request, "Método no permitido.")
    
    return redirect('lista_calificaciones')


@login_required
def previsualizar_informe_individual(request, estudiante_id, periodo):
    if request.user.rol != 'admin':
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    calificaciones = Calificacion.objects.filter(estudiante=estudiante, periodo_id=periodo)
    promedio_general = calificaciones.aggregate(Avg('nota'))['nota__avg'] or 0
    context = {
        'estudiante_seleccionado': estudiante,
        'calificaciones_estudiante': calificaciones,
        'promedio_general': round(promedio_general, 2),
        'periodo': get_object_or_404(Periodo, id=periodo),
    }
    return render(request, 'academico/informes/previsualizacion_individual.html', context)

@login_required
def informes_rendimiento(request):
    if request.user.rol != 'admin':
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')
    periodos = Periodo.objects.all()
    asignaturas = Asignatura.objects.all()
    estudiantes = Estudiante.objects.all()
    periodo_seleccionado = request.GET.get('periodo')
    asignatura_seleccionada_id = request.GET.get('asignatura')
    estudiante_seleccionado_id = request.GET.get('estudiante')
    calificaciones = Calificacion.objects.all()
    calificaciones_estudiante = None
    calificaciones_grupo = None
    informe_individual = False
    informe_grupal = False
    estudiante_seleccionado = None
    asignatura_seleccionada = None
    if periodo_seleccionado:
        calificaciones = calificaciones.filter(periodo_id=periodo_seleccionado)
    if estudiante_seleccionado_id:
        try:
            estudiante_seleccionado = Estudiante.objects.get(id=estudiante_seleccionado_id)
            calificaciones_estudiante = calificaciones.filter(estudiante_id=estudiante_seleccionado_id)
            informe_individual = True
        except Estudiante.DoesNotExist:
            calificaciones_estudiante = None
            informe_individual = False
    if asignatura_seleccionada_id:
        try:
            asignatura_seleccionada = Asignatura.objects.get(id=asignatura_seleccionada_id)
            calificaciones_grupo = calificaciones.filter(asignatura_id=asignatura_seleccionada_id)
            informe_grupal = True
        except Asignatura.DoesNotExist:
            calificaciones_grupo = None
            informe_grupal = False
    total_estudiantes = calificaciones.values('estudiante').distinct().count()
    promedio_general = calificaciones.aggregate(Avg('nota'))['nota__avg'] or 0
    aprobados = calificaciones.filter(nota__gte=3.0).count()
    reprobados = calificaciones.filter(nota__lt=3.0).count()
    context = {
        'periodos': periodos,
        'asignaturas': asignaturas,
        'estudiantes': estudiantes,
        'periodo_seleccionado': periodo_seleccionado,
        'asignatura_seleccionada': asignatura_seleccionada,
        'estudiante_seleccionado': estudiante_seleccionado,
        'calificaciones_estudiante': calificaciones_estudiante,
        'calificaciones_grupo': calificaciones_grupo,
        'informe_individual': informe_individual and calificaciones_estudiante is not None,
        'informe_grupal': informe_grupal and calificaciones_grupo is not None,
        'total_estudiantes': total_estudiantes,
        'promedio_general': round(promedio_general, 2),
        'aprobados': aprobados,
        'reprobados': reprobados,
    }
    return render(request, 'academico/informes/informes_rendimiento.html', context)

@login_required
def exportar_pdf_individual(request, estudiante_id):
    try:
        estudiante = get_object_or_404(Estudiante, id=estudiante_id)
        calificaciones = Calificacion.objects.filter(estudiante=estudiante).select_related('asignatura', 'periodo')
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"Informe de Calificaciones - {estudiante.user.get_full_name()}")
        y = 700
        for calificacion in calificaciones:
            texto = f"{calificacion.asignatura.nombre}: {calificacion.nota:.2f}"
            p.drawString(100, y, texto)
            y -= 20
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=informe_{estudiante.user.username}.pdf'
        return response
    except Exception as e:
        messages.error(request, f"Error al generar el PDF: {str(e)}")
        return redirect('informes_rendimiento')

@login_required
def exportar_excel_individual(request, estudiante_id):
    try:
        estudiante = get_object_or_404(Estudiante, id=estudiante_id)
        calificaciones = Calificacion.objects.filter(estudiante=estudiante).select_related('asignatura', 'periodo')
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        header_format = workbook.add_format({'bold': True, 'bg_color': '#4B5563', 'font_color': 'white'})
        headers = ['Asignatura', 'Período', 'Nota']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        for row, calificacion in enumerate(calificaciones, start=1):
            worksheet.write(row, 0, calificacion.asignatura.nombre)
            worksheet.write(row, 1, calificacion.periodo.nombre)
            worksheet.write(row, 2, float(calificacion.nota))
        workbook.close()
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=calificaciones_{estudiante.user.username}.xlsx'
        return response
    except Exception as e:
        messages.error(request, f"Error al generar el Excel: {str(e)}")
        return redirect('informes_rendimiento')

@login_required
def exportar_pdf_grupal(request, asignatura_id):
    try:
        asignatura = get_object_or_404(Asignatura, id=asignatura_id)
        calificaciones = Calificacion.objects.filter(asignatura=asignatura).select_related('estudiante__user')
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"Informe Grupal - {asignatura.nombre}")
        y = 700
        for calificacion in calificaciones:
            texto = f"{calificacion.estudiante.user.get_full_name()}: {calificacion.nota:.2f}"
            p.drawString(100, y, texto)
            y -= 20
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=informe_grupal_{asignatura.nombre}.pdf'
        return response
    except Exception as e:
        messages.error(request, f"Error al generar el PDF grupal: {str(e)}")
        return redirect('informes_rendimiento')

@login_required
def exportar_excel_grupal(request, asignatura_id):
    try:
        asignatura = get_object_or_404(Asignatura, id=asignatura_id)
        calificaciones = Calificacion.objects.filter(asignatura=asignatura).select_related('estudiante__user', 'periodo')
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        header_format = workbook.add_format({'bold': True, 'bg_color': '#4B5563', 'font_color': 'white'})
        headers = ['Estudiante', 'Período', 'Nota']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        for row, calificacion in enumerate(calificaciones, start=1):
            worksheet.write(row, 0, calificacion.estudiante.user.get_full_name())
            worksheet.write(row, 1, calificacion.periodo.nombre)
            worksheet.write(row, 2, float(calificacion.nota))
        workbook.close()
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=calificaciones_grupo_{asignatura.nombre}.xlsx'
        return response
    except Exception as e:
        messages.error(request, f"Error al generar el Excel grupal: {str(e)}")
        return redirect('informes_rendimiento')

def tu_vista(request):
    # Add your view logic here
    return redirect('login')  # or whatever response you want to return
