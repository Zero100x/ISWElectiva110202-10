from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        """
        Crea y devuelve un usuario normal con el rol asignado.
        """
        if not username:
            raise ValueError('El usuario debe tener un nombre de usuario')

        # Aquí obtenemos el valor de 'rol' de `extra_fields` si existe
        rol = extra_fields.get('rol', 'estudiante')  # Rol predeterminado a 'estudiante'
        if rol not in ['admin', 'profesor', 'estudiante']:
            raise ValueError('Rol debe ser: admin, profesor o estudiante')

        # Crear el usuario, asegurándonos de que 'rol' se pase a través de `extra_fields`
        user = self.model(username=username, **extra_fields)
        user.is_staff = rol in ['admin', 'profesor']
        user.is_superuser = rol == 'admin'
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Crea y devuelve un superusuario con el rol 'admin'.
        """
        extra_fields.setdefault('rol', 'admin')  # Aseguramos que el rol sea 'admin' para el superusuario
        return self.create_user(username, password, **extra_fields)

class User(AbstractUser):
    ROLES = [('admin', 'Administrador'), ('profesor', 'Profesor'), ('estudiante', 'Estudiante')]
    
    username = models.CharField('Nombre de usuario', max_length=30, unique=True)
    rol = models.CharField('Rol', max_length=20, choices=ROLES, default='estudiante')
    pregunta_seguridad = models.CharField('Pregunta de recuperación', max_length=200, blank=True, null=True)
    respuesta_seguridad = models.CharField('Respuesta de recuperación', max_length=200, blank=True, null=True)
    primer_inicio_sesion = models.BooleanField(default=True)
    intentos_recuperacion = models.IntegerField(default=0)
    ultimo_intento = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['rol']  # Aseguramos que 'rol' sea un campo obligatorio

    def __str__(self):
        return self.username

    def get_pregunta_seguridad(self):
        return self.pregunta_seguridad or "No registrada"



# Student Model
class Estudiante(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Subject Model
class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# Period Model
class Periodo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# Professor Model
class Profesor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Grade Model
class Calificacion(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['estudiante', 'asignatura']),
            models.Index(fields=['periodo']),
            models.Index(fields=['profesor'])
        ]
        ordering = ['-periodo__nombre', 'asignatura__nombre']

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    tipo_evaluacion = models.CharField(max_length=50, default="Final")
    nombre = models.CharField(
        max_length=100, 
        blank=False,  # Puedes cambiar a False si lo quieres requerido
        verbose_name="Nombre/Descripción",
        help_text="Nombre descriptivo de la calificación"
    )
    nota = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        if self.nombre:
            return f"{self.nombre} - {self.nota}"
        return f"{self.tipo_evaluacion} - {self.estudiante} - {self.nota}"
