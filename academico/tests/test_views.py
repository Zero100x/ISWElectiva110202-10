import json
from django.test import TestCase, RequestFactory
from academico.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# Corregir las importaciones usando la ruta completa
from academico.models import Asignatura, Periodo, Profesor, Estudiante, Calificacion
from academico.forms import SecurityConfigForm

class TestViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        self.admin_user = User.objects.create_user(
            username='admin', password='admin123', rol='admin'
        )
        self.profesor_user = User.objects.create_user(
            username='profesor', password='profesor123', rol='profesor',
            pregunta_seguridad="Pregunta", respuesta_seguridad="Respuesta"
        )
        self.estudiante_user = User.objects.create_user(
            username='estudiante', password='estudiante123', rol='estudiante',
            pregunta_seguridad="Pregunta", respuesta_seguridad="Respuesta"
        )
        
        self.profesor = Profesor.objects.create(user=self.profesor_user)
        self.estudiante = Estudiante.objects.create(user=self.estudiante_user)
        self.periodo = Periodo.objects.create(nombre="2023-1", fecha_inicio=timezone.now())
        self.asignatura = Asignatura.objects.create(nombre="Matemáticas")
        self.calificacion = Calificacion.objects.create(
            estudiante=self.estudiante,
            profesor=self.profesor,
            asignatura=self.asignatura,
            periodo=self.periodo,
            nota=4.5
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_view_post_success(self):
        data = {'username': 'profesor', 'password': 'profesor123'}
        response = self.client.post(reverse('login'), data)
        self.assertRedirects(response, reverse('lista_calificaciones'))