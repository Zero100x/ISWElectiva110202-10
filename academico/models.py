from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Gestor personalizado para el modelo de usuario
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, rol='estudiante', pregunta_seguridad=None, respuesta_seguridad=None):
        if not username:
            raise ValueError('El usuario debe tener un nombre de usuario')
        
        # Validación del rol
        if rol not in ['admin', 'profesor', 'estudiante']:
            raise ValueError('Rol debe ser: admin, profesor o estudiante')
            
        user = self.model(
            username=username,
            rol=rol,
            pregunta_seguridad=pregunta_seguridad,
            respuesta_seguridad=respuesta_seguridad
        )
        
        # Configuración específica según el rol
        if rol == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif rol == 'profesor':
            user.is_staff = True
            user.is_superuser = False
        else:  # estudiante
            user.is_staff = False
            user.is_superuser = False
            
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, rol='admin', pregunta_seguridad=None, respuesta_seguridad=None):
        # Forzar rol admin para superusuarios
        if rol != 'admin':
            rol = 'admin'
            
        user = self.create_user(
            username=username,
            password=password,
            rol=rol,
            pregunta_seguridad=pregunta_seguridad,
            respuesta_seguridad=respuesta_seguridad
        )
        return user

# Modelo personalizado de Usuario
class User(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
    )
    username = models.CharField('Nombre de usuario', max_length=30, unique=True)
    rol = models.CharField('Rol', max_length=20, choices=ROLES, default='estudiante')
    pregunta_seguridad = models.CharField('Pregunta de recuperación', max_length=200, blank=True, null=True)
    respuesta_seguridad = models.CharField('Respuesta de recuperación', max_length=200, blank=True, null=True)
    primer_inicio_sesion = models.BooleanField(default=True)
    intentos_recuperacion = models.IntegerField(default=0)
    ultimo_intento = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['rol']

    def __str__(self):
        return self.username
        
    def get_pregunta_seguridad(self):
        return self.pregunta_seguridad or "No registrada"

# Modelo de Estudiante
class Estudiante(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

# Modelo de Asignatura
class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Modelo de Periodo
class Periodo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Modelo de Profesor
# Remove this import
# from django.contrib.auth.models import User

class Profesor(models.Model):
    user = models.OneToOneField('academico.User', on_delete=models.CASCADE)
    # Otros campos adicionales para Profesor pueden ir aquí

    def __str__(self):
        return self.user.get_full_name() or self.user.username

# Modelo de Calificación
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
    tipo_evaluacion = models.CharField(max_length=50, default="Final")  # Ej: Parcial, Final, etc.
    nota = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} - {self.periodo}: {self.nota}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.rol == 'profesor':
        Profesor.objects.create(user=instance)
ROLES = (
    ('admin', 'Administrador'),
    ('profesor', 'Profesor'),
    ('estudiante', 'Estudiante'),
)