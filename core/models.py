"""
Modelos de la aplicación core.

Este archivo define los modelos de datos que representan las entidades
principales de la aplicación.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

class User(AbstractUser):
    """
    Modelo de usuario personalizado.
    
    Extiende el modelo de usuario de Django para incluir roles específicos
    que determinan los permisos y accesos en la aplicación.
    
    Roles disponibles:
    - Estudiante: acceso a funcionalidades de aprendizaje
    - Profesor: puede crear contenido y evaluar estudiantes
    - Administrador: acceso completo a todas las funcionalidades
    """
    # Constantes para los roles de usuario
    STUDENT = 'student'
    TEACHER = 'teacher'
    ADMIN = 'admin'
    
    # Opciones para el campo de rol
    ROLE_CHOICES = [
        (STUDENT, 'Estudiante'),
        (TEACHER, 'Profesor'),
        (ADMIN, 'Administrador'),
    ]
    
    # Campo para almacenar el rol del usuario
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=STUDENT,
        verbose_name='Rol',
        help_text='Determina los permisos y accesos del usuario'
    )
    
    def __str__(self):
        """Representación en texto del usuario"""
        return f"{self.username} ({self.get_role_display()})"
    
    def get_absolute_url(self):
        """
        Devuelve la URL del dashboard según el rol del usuario.
        
        Esta función se usa para redireccionar al usuario después del login.
        """
        if self.role == self.ADMIN:
            return reverse('admin_dashboard')
        elif self.role == self.TEACHER:
            return reverse('teacher_dashboard')
        return reverse('student_dashboard')
    
    # Métodos para facilitar la verificación de roles
    
    def is_student(self):
        """Verifica si el usuario tiene rol de estudiante"""
        return self.role == self.STUDENT
    
    def is_teacher(self):
        """Verifica si el usuario tiene rol de profesor"""
        return self.role == self.TEACHER
    
    def is_admin(self):
        """Verifica si el usuario tiene rol de administrador"""
        return self.role == self.ADMIN
    
    def has_role(self, role):
        """Verifica si el usuario tiene un rol específico"""
        return self.role == role
    
    def has_any_role(self, roles):
        """Verifica si el usuario tiene alguno de los roles especificados"""
        return self.role in roles
    
    def can_access_student_content(self):
        """Verifica si el usuario puede acceder a contenido de estudiantes"""
        return True  # Todos los roles pueden acceder
    
    def can_access_teacher_content(self):
        """Verifica si el usuario puede acceder a contenido de profesores"""
        return self.role in [self.TEACHER, self.ADMIN]
    
    def can_access_admin_content(self):
        """Verifica si el usuario puede acceder a contenido de administradores"""
        return self.role == self.ADMIN
    
    def get_dashboard_url(self):
        """Retorna la URL del dashboard del usuario según su rol"""
        return self.get_absolute_url()

# Puedes añadir más modelos según las necesidades de tu aplicación
