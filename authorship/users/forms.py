from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

# Clase formulario genérico
class BaseRegistroForm(UserCreationForm):
    #Se fuerza a que el campo email sea obligatorio
    email = forms.EmailField(required=True, help_text="Requerido para notificaciones.")
    
    class Meta(UserCreationForm.Meta):
        model = User
        #Se utilizan los campos del formulario de django y además el campo email
        fields = UserCreationForm.Meta.fields + ('email',)

# Registro de autores: extiende el formulario base con campos de perfil profesional
class AutorRegistroForm(BaseRegistroForm):
    # Se crea un campo de texto para la biografía del autor
    biography = forms.CharField(
        # Es un campo obligatorio
        required=True,
        help_text="Cuéntanos sobre tu trayectoria creativa."
    )

    class Meta(BaseRegistroForm.Meta):
        fields = BaseRegistroForm.Meta.fields + ('biography',)

# Registro de consumidores: extiende el formulario base con campos sobre intereses
class ConsumidorRegistroForm(BaseRegistroForm):
    # Se crea un campo de texto para los intereses del consumidor
    interests = forms.CharField(
        max_length=200, 
        # No es un campo obligatorio
        required=False,
        help_text="Ej: Música, Literatura, Software..."
    )

    class Meta(BaseRegistroForm.Meta):
        fields = BaseRegistroForm.Meta.fields + ('interests',)