import os
import shutil
from pathlib import Path

def reset_migrations():
    """
    Script para eliminar todas las migraciones y recrear la base de datos desde cero.
    """
    # Eliminar archivo de base de datos si existe
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("✓ Base de datos eliminada")
    
    # Buscar y eliminar directorios de migraciones
    for root, dirs, files in os.walk('.'):
        if 'migrations' in dirs:
            migrations_dir = os.path.join(root, 'migrations')
            # Conservar el archivo __init__.py
            init_file = os.path.join(migrations_dir, '__init__.py')
            has_init = os.path.exists(init_file)
            
            # Eliminar todos los archivos de migración
            for item in os.listdir(migrations_dir):
                if item != '__init__.py':
                    item_path = os.path.join(migrations_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            
            print(f"✓ Migraciones eliminadas en {migrations_dir}")
            
            # Recrear __init__.py si existía
            if has_init and not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    pass
    
    print("\nProceso completado. Ahora ejecuta los siguientes comandos:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python manage.py createsuperuser")

if __name__ == "__main__":
    reset_migrations()