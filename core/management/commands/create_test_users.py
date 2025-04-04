"""
Comando personalizado de Django para crear usuarios de prueba.

Este script permite crear rápidamente usuarios con diferentes roles para
propósitos de testing y desarrollo.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea usuarios de prueba con diferentes roles (estudiante, profesor, administrador)'

    def add_arguments(self, parser):
        # Argumentos nombrados opcionales
        parser.add_argument(
            '--admin',
            action='store_true',
            help='Crear usuario administrador',
        )
        
        parser.add_argument(
            '--teacher',
            action='store_true',
            help='Crear usuario profesor',
        )
        
        parser.add_argument(
            '--student',
            action='store_true',
            help='Crear usuario estudiante',
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Crear un usuario de cada rol',
        )
        
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Número de usuarios a crear por cada rol seleccionado',
        )
        
        parser.add_argument(
            '--password',
            type=str,
            default='password123',
            help='Contraseña para los usuarios creados',
        )

    def handle(self, *args, **options):
        password = options['password']
        count = options['count']
        
        # Definir qué tipos de usuarios crear
        create_admin = options['admin'] or options['all']
        create_teacher = options['teacher'] or options['all']
        create_student = options['student'] or options['all']
        
        # Si no se especifica ningún tipo, crear uno de cada por defecto
        if not any([create_admin, create_teacher, create_student]):
            create_admin = create_teacher = create_student = True
        
        # Función auxiliar para crear usuarios
        def create_users(role, role_name, count):
            created_users = []
            
            for i in range(1, count + 1):
                # Crear nombre de usuario único
                suffix = get_random_string(4).lower() if count > 1 else ''
                username = f"{role}_{suffix}" if suffix else role
                
                # Verificar si el usuario ya existe
                if User.objects.filter(username=username).exists():
                    username = f"{role}_{get_random_string(6).lower()}"
                
                # Crear el usuario
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password=password,
                    first_name=role_name,
                    last_name=f"Usuario {i}",
                    role=role
                )
                
                created_users.append(user)
                self.stdout.write(self.style.SUCCESS(
                    f'Usuario creado con éxito: {username} (Rol: {role_name})'
                ))
            
            return created_users
        
        # Crear usuarios según los argumentos proporcionados
        if create_admin:
            admins = create_users(User.ADMIN, 'Administrador', count)
        
        if create_teacher:
            teachers = create_users(User.TEACHER, 'Profesor', count)
        
        if create_student:
            students = create_users(User.STUDENT, 'Estudiante', count)
        
        # Resumen final
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Resumen de usuarios creados:'))
        
        if create_admin:
            self.stdout.write(self.style.SUCCESS(f'- Administradores: {count}'))
        
        if create_teacher:
            self.stdout.write(self.style.SUCCESS(f'- Profesores: {count}'))
        
        if create_student:
            self.stdout.write(self.style.SUCCESS(f'- Estudiantes: {count}'))
        
        self.stdout.write(self.style.SUCCESS(f'Contraseña para todos: {password}'))
        self.stdout.write(self.style.SUCCESS('='*50))