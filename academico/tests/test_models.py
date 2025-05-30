import pytest
from django.contrib.auth import get_user_model
from academico.models import Estudiante, Profesor, Asignatura, Periodo, Calificacion

User = get_user_model()

@pytest.mark.django_db
def test_creacion_usuario_personalizado():
    user = User.objects.create_user(username="zero", password="clave123", rol="profesor")
    assert user.username == "zero"
    assert user.rol == "profesor"
    assert user.check_password("clave123")

@pytest.mark.django_db
def test_get_pregunta_seguridad():
    user = User.objects.create_user(username="zero2", password="clave123")
    assert user.get_pregunta_seguridad() == "No registrada"
    user.pregunta_seguridad = "¿Color favorito?"
    user.save()
    assert user.get_pregunta_seguridad() == "¿Color favorito?"

@pytest.mark.django_db
def test_modelos_relacionados():
    user_estudiante = User.objects.create_user(username="est1", password="123")
    estudiante = Estudiante.objects.create(user=user_estudiante, matricula="MAT123")

    user_profesor = User.objects.create_user(username="prof1", password="123", rol="profesor")
    profesor = Profesor.objects.create(user=user_profesor)

    asignatura = Asignatura.objects.create(nombre="Matemáticas")
    periodo = Periodo.objects.create(nombre="2025-1")

    calificacion = Calificacion.objects.create(
        estudiante=estudiante,
        profesor=profesor,
        asignatura=asignatura,
        periodo=periodo,
        nombre="Parcial 1",
        nota=4.5
    )

    assert str(estudiante) == "est1"
    assert str(profesor) == "prof1"
    assert str(asignatura) == "Matemáticas"
    assert str(periodo) == "2025-1"
    assert str(calificacion) == "Parcial 1 - 4.5"
