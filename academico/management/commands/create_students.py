from django.core.management.base import BaseCommand
from academico.models import User, Estudiante
from django.db import IntegrityError
import uuid

class Command(BaseCommand):
    help = 'Create Estudiante instances for all users with the role student ensuring unique matricula'

    def handle(self, *args, **kwargs):
        estudiantes_count = 0
        errors_count = 0
        
        # Get all users with the role 'estudiante'
        for user in User.objects.filter(rol='estudiante'):
            # Check if the Estudiante instance already exists
            if not Estudiante.objects.filter(user=user).exists():
                success = False
                retries = 0
                max_retries = 5
                
                while not success and retries < max_retries:
                    # Generate a unique matricula with user ID and random suffix
                    matricula = f"MAT-{user.id}-{uuid.uuid4().hex[:6]}"
                    
                    try:
                        # Create an Estudiante instance for the user with the generated matricula
                        Estudiante.objects.create(user=user, matricula=matricula)
                        estudiantes_count += 1
                        success = True
                        self.stdout.write(self.style.SUCCESS(f'Created Estudiante for {user.username} with matricula {matricula}'))
                    except IntegrityError as e:
                        retries += 1
                        self.stdout.write(self.style.WARNING(f'Attempt {retries}/{max_retries}: Failed to create Estudiante for {user.username} due to: {e}'))
                
                if not success:
                    errors_count += 1
                    self.stdout.write(self.style.ERROR(f'Failed to create Estudiante for {user.username} after {max_retries} attempts'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {estudiantes_count} Estudiante instances'))
        if errors_count > 0:
            self.stdout.write(self.style.WARNING(f'Failed to create {errors_count} Estudiante instances due to persistent errors'))
