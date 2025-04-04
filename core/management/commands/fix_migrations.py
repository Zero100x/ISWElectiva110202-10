from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Corrige el historial de migraciones inconsistentes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando corrección de migraciones...'))
        
        with connection.cursor() as cursor:
            # Verificamos si las migraciones existen
            cursor.execute("""
                SELECT id, app, name, applied 
                FROM django_migrations 
                WHERE (app='admin' AND name='0001_initial') 
                   OR (app='core' AND name='0001_initial')
                ORDER BY applied;
            """)
            
            migrations = cursor.fetchall()
            if len(migrations) < 1:
                self.stdout.write(self.style.WARNING('No se encontraron las migraciones necesarias.'))
                return
            
            for migration in migrations:
                self.stdout.write(f"ID: {migration[0]}, App: {migration[1]}, Name: {migration[2]}, Applied: {migration[3]}")
            
            # Verificamos si core.0001_initial ya existe
            cursor.execute("""
                SELECT id FROM django_migrations 
                WHERE app='core' AND name='0001_initial';
            """)
            core_result = cursor.fetchone()
            
            if core_result:
                self.stdout.write(self.style.WARNING('La migración core.0001_initial ya existe en la base de datos.'))
                
                # Obtenemos el ID de la migración admin.0001_initial
                cursor.execute("""
                    SELECT id FROM django_migrations 
                    WHERE app='admin' AND name='0001_initial';
                """)
                admin_result = cursor.fetchone()
                
                if admin_result:
                    admin_id = admin_result[0]
                    
                    # Actualizamos la fecha de aplicación de admin.0001_initial
                    cursor.execute("""
                        UPDATE django_migrations 
                        SET applied = (
                            SELECT datetime(applied, '+1 second') 
                            FROM django_migrations 
                            WHERE app='core' AND name='0001_initial'
                        )
                        WHERE id = ?;
                    """, [admin_id])
                    
                    self.stdout.write(self.style.SUCCESS('Historial de migraciones corregido. admin.0001_initial ahora aparece después de core.0001_initial.'))
                else:
                    self.stdout.write(self.style.ERROR('No se encontró la migración admin.0001_initial.'))
            else:
                # Insertamos core.0001_initial como aplicada
                self.stdout.write(self.style.WARNING('La migración core.0001_initial no está en la base de datos. Insertándola...'))
                
                # Obtenemos la fecha más antigua de migración
                cursor.execute("SELECT MIN(applied) FROM django_migrations WHERE app='admin' AND name='0001_initial';")
                admin_date = cursor.fetchone()[0]
                
                if admin_date:
                    # Insertamos core.0001_initial con una fecha anterior
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied)
                        VALUES ('core', '0001_initial', datetime(?, '-1 second'));
                    """, [admin_date])
                    
                    self.stdout.write(self.style.SUCCESS('Migración core.0001_initial marcada como aplicada antes que admin.0001_initial.'))
                else:
                    self.stdout.write(self.style.ERROR('No se pudo determinar la fecha de aplicación de admin.0001_initial.'))
        
        self.stdout.write(self.style.SUCCESS('Proceso completado. Ahora intenta ejecutar "python manage.py migrate" nuevamente.'))