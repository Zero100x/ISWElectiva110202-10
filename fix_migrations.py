from django.db import connection

def fix_migration_history():
    """
    Script para corregir el historial de migraciones inconsistentes.
    Específicamente, actualiza la fecha de aplicación de admin.0001_initial
    para que aparezca después de core.0001_initial.
    """
    with connection.cursor() as cursor:
        # Primero, verificamos si la tabla django_migrations existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='django_migrations';
        """)
        if not cursor.fetchone():
            print("La tabla django_migrations no existe.")
            return

        # Verificamos si las migraciones existen
        cursor.execute("""
            SELECT id, app, name, applied 
            FROM django_migrations 
            WHERE (app='admin' AND name='0001_initial') 
               OR (app='core' AND name='0001_initial')
            ORDER BY applied;
        """)
        
        migrations = cursor.fetchall()
        if len(migrations) < 2:
            print("No se encontraron ambas migraciones.")
            return
        
        for migration in migrations:
            print(f"ID: {migration[0]}, App: {migration[1]}, Name: {migration[2]}, Applied: {migration[3]}")
        
        # Obtenemos el ID de la migración admin.0001_initial
        cursor.execute("""
            SELECT id FROM django_migrations 
            WHERE app='admin' AND name='0001_initial';
        """)
        admin_id = cursor.fetchone()[0]
        
        # Obtenemos la fecha de aplicación de core.0001_initial
        cursor.execute("""
            SELECT applied FROM django_migrations 
            WHERE app='core' AND name='0001_initial';
        """)
        core_date_result = cursor.fetchone()
        
        if not core_date_result:
            print("La migración core.0001_initial no está en la base de datos.")
            print("Intentando insertar core.0001_initial como aplicada...")
            
            # Obtenemos la fecha más reciente
            cursor.execute("SELECT MAX(applied) FROM django_migrations;")
            latest_date = cursor.fetchone()[0]
            
            # Insertamos core.0001_initial como aplicada
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('core', '0001_initial', ?);
            """, [latest_date])
            
            print("Migración core.0001_initial marcada como aplicada.")
            return
        
        # Actualizamos la fecha de aplicación de admin.0001_initial
        # para que sea posterior a core.0001_initial
        cursor.execute("""
            UPDATE django_migrations 
            SET applied = (
                SELECT datetime(applied, '+1 second') 
                FROM django_migrations 
                WHERE app='core' AND name='0001_initial'
            )
            WHERE id = ?;
        """, [admin_id])
        
        print("Historial de migraciones corregido. admin.0001_initial ahora aparece después de core.0001_initial.")

if __name__ == "__main__":
    fix_migration_history()
    print("Ahora intenta ejecutar 'python manage.py migrate' nuevamente.")