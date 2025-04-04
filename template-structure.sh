# Estructura recomendada para tus plantillas
# Asegúrate de que tu plantilla de login esté en esta ubicación

project_root/
├── classmate/
│   └── urls.py
├── core/
│   ├── templates/
│   │   ├── registration/
│   │   │   └── login.html  # Tu nueva plantilla de login con fondo rojo
│   │   └── core/
│   │       └── otros_templates.html
│   ├── urls.py
│   └── views.py
└── templates/  # Directorio de plantillas a nivel de proyecto
    └── registration/
        └── login.html  # Alternativa: ubicar aquí tu plantilla