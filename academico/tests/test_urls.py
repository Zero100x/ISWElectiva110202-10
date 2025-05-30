import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_urls_resolucion(client, django_user_model):
    # Crear un usuario de prueba si es necesario para login
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')

    rutas = [
        'login',
        'logout',
        'lista_calificaciones',
        'calificaciones_estudiante',
        'recuperar_contrasena_usuario',
        'recuperar_contrasena_pregunta',
        'recuperar_contrasena_reset',
        'configurar_seguridad',
        'crear_asignatura',
        'crear_calificacion',
        'informes_rendimiento',
    ]

    for nombre in rutas:
        url = reverse(nombre)
        response = client.get(url)
        assert response.status_code in [200, 302, 403, 405]  # válidos dependiendo de lógica de login y método

@pytest.mark.django_db
def test_urls_con_parametros(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser', password='testpass')
    client.login(username='testuser', password='testpass')

    # Estas pruebas necesitan objetos en la DB: estudiante_id, asignatura_id, etc.
    from academico.models import Estudiante, Asignatura, Calificacion, Periodo
    estudiante = Estudiante.objects.create(nombre="Juan", apellido="Pérez")
    asignatura = Asignatura.objects.create(nombre="Matemáticas")
    periodo = Periodo.objects.create(nombre="2024-A")

    reverse_urls = [
        reverse('exportar_pdf_individual', args=[estudiante.id]),
        reverse('exportar_excel_individual', args=[estudiante.id]),
        reverse('exportar_pdf_grupal', args=[asignatura.id]),
        reverse('exportar_excel_grupal', args=[asignatura.id]),
        reverse('previsualizar_informe_individual', args=[estudiante.id, periodo.id]),
    ]

    for url in reverse_urls:
        response = client.get(url)
        assert response.status_code in [200, 302, 403, 404]
