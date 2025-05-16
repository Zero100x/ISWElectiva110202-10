from django.test import TestCase, Client
from django.urls import reverse
from academico.models import User, Asignatura, Calificacion, Periodo, Profesor, Estudiante
from .forms import (
    LoginForm, RecuperacionUsuarioForm, RecuperacionPreguntaForm,
    RecuperacionPasswordForm, SecurityConfigForm, AsignaturaForm, CalificacionForm
)

class AcademicViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', rol='profesor')
        self.profesor = Profesor.objects.create(user=self.user)
        self.estudiante = Estudiante.objects.create(user=self.user)
        self.asignatura = Asignatura.objects.create(nombre='Matemáticas')
        self.periodo = Periodo.objects.create(nombre='2023-1')
        self.calificacion = Calificacion.objects.create(
            profesor=self.profesor,
            estudiante=self.estudiante,
            asignatura=self.asignatura,
            periodo=self.periodo,
            nota=4.5
        )

    def test_login_view(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect after logout

    def test_configurar_seguridad(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('configurar_seguridad'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academico/configurar_seguridad.html')

    def test_recuperar_contrasena_usuario(self):
        response = self.client.get(reverse('recuperar_contrasena_usuario'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academico/recuperar_usuario.html')

    def test_lista_calificaciones(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('lista_calificaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academico/lista_calificaciones.html')

    def test_calificaciones_estudiante(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('calificaciones_estudiante'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academico/calificaciones_estudiante.html')

    def test_editar_calificacion(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('editar_calificacion', args=[self.calificacion.id]),
            data=json.dumps({'nota': 5.0}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.calificacion.refresh_from_db()
        self.assertEqual(self.calificacion.nota, 5.0)

    def test_crear_asignatura_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('crear_asignatura'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academico/crear_asignatura.html')

    def test_crear_calificacion_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('crear_calificacion'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academico/crear_calificacion.html')

    def test_informes_rendimiento(self):
        admin_user = User.objects.create_user(username='admin', password='adminpass', rol='admin')
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('informes_rendimiento'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'academico/informes_rendimiento.html')

    def test_exportar_pdf_individual(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('exportar_pdf_individual', args=[self.estudiante.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_exportar_excel_individual(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('exportar_excel_individual', args=[self.estudiante.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_exportar_pdf_grupal(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('exportar_pdf_grupal', args=[self.asignatura.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_exportar_excel_grupal(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('exportar_excel_grupal', args=[self.asignatura.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
