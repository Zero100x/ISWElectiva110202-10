from django import forms
from .models import Asignatura, Calificacion, Estudiante, Periodo

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=150)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


class RecuperacionUsuarioForm(forms.Form):
    """
    Primer paso: Formulario para ingresar el nombre de usuario a recuperar
    """
    username = forms.CharField(label="Usuario", max_length=150)


class RecuperacionPreguntaForm(forms.Form):
    """
    Segundo paso: Formulario para responder la pregunta de seguridad
    """
    pregunta_seguridad = forms.CharField(
        label="Pregunta de seguridad",
        required=False,
        disabled=True
    )
    respuesta_seguridad = forms.CharField(
        label="Respuesta de seguridad",
        max_length=200,
        widget=forms.PasswordInput
    )


class PasswordValidationMixin:
    def validate_password(self, password1, password2):
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        if password1 and len(password1) < 6:
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")

class RecuperacionPasswordForm(forms.Form, PasswordValidationMixin):
    """
    Tercer paso: Formulario para establecer la nueva contraseña
    """
    nueva_contrasena = forms.CharField(
        label="Nueva contraseña",
        max_length=100,
        widget=forms.PasswordInput
    )
    confirmar_contrasena = forms.CharField(
        label="Confirmar nueva contraseña",
        max_length=100,
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("nueva_contrasena")
        password2 = cleaned_data.get("confirmar_contrasena")
        self.validate_password(password1, password2)
        return cleaned_data


class SecurityConfigForm(forms.Form):
    """
    Formulario para configurar preguntas y respuestas de seguridad durante el primer inicio de sesión.
    """
    pregunta_seguridad = forms.CharField(
        max_length=200,
        label="Pregunta de seguridad",
        help_text="Establezca una pregunta de seguridad única y memorable para recuperar su cuenta"
    )
    respuesta_seguridad = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput,
        label="Respuesta de seguridad",
        help_text="Esta respuesta será requerida si necesita recuperar su contraseña. Asegúrese de recordarla."
    )
    confirmar_respuesta = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput,
        label="Confirmar respuesta"
    )

    def clean(self):
        cleaned_data = super().clean()
        respuesta = cleaned_data.get("respuesta_seguridad")
        confirmar = cleaned_data.get("confirmar_respuesta")

        if respuesta and confirmar and respuesta != confirmar:
            raise forms.ValidationError("Las respuestas de seguridad no coinciden.")
        return cleaned_data


class ResetPasswordForm(forms.Form):
    """
    Formulario adicional para recuperación de contraseña directamente desde email u otro mecanismo.
    """
    new_password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva contraseña'})
    )
    confirm_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        if new_password and len(new_password) < 6:
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        def save(self, commit=True):
            user = super().save(commit=False)
            if commit:
                user.save()
                if user.rol == 'profesor':
                    Profesor.objects.create(user=user)
            return user
        return cleaned_data
    
class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'})
        }

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['nombre', 'estudiante', 'asignatura', 'periodo', 'nota']  # Agregar 'nombre'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'border-gray-300 rounded p-2 w-full',
                'placeholder': 'Ej: Examen parcial Unidad 2'
            }),
            'estudiante': forms.Select(attrs={
                'class': 'border-gray-300 rounded p-2 w-full'
            }),
            'asignatura': forms.Select(attrs={
                'class': 'border-gray-300 rounded p-2 w-full'
            }),
            'periodo': forms.Select(attrs={
                'class': 'border-gray-300 rounded p-2 w-full'
            }),
            'nota': forms.NumberInput(attrs={
                'class': 'border-gray-300 rounded p-2 w-full',
                'step': '0.1',
                'min': '0',
                'max': '5'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        profesor = kwargs.pop('profesor', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar asignaturas y estudiantes según el profesor
        if profesor:
            self.fields['asignatura'].queryset = profesor.asignaturas.all()
            self.fields['estudiante'].queryset = Estudiante.objects.filter(
                asignaturas__profesor=profesor
            ).distinct()
        
        # Opciones para tipo de evaluación
        self.fields['tipo_evaluacion'].widget.choices = [
            ('', 'Seleccione un tipo'),
            ('Parcial', 'Parcial'),
            ('Final', 'Final'),
            ('Quiz', 'Quiz'),
            ('Trabajo', 'Trabajo Práctico'),
            ('Proyecto', 'Proyecto'),
            ('Otro', 'Otro'),
        ]
        
        # Hacer que el campo nombre sea requerido
        self.fields['nombre'].required = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['estudiante'].disabled = True
        
        


    