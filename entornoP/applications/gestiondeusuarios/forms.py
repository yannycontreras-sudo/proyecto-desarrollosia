from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model



User = get_user_model()


class RegistroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()

        if not email:
            raise ValidationError("Este campo es obligatorio.")

        try:
            _, domain = email.split("@", 1)
        except ValueError:
            raise ValidationError("Correo electrónico inválido.")

        allowed_domains = ("ucn.cl", "alumnos.ucn.cl")
        if domain not in allowed_domains:
            raise ValidationError("Solo se permiten correos @ucn.cl o @alumnos.ucn.cl.")

        return email

class LoginForm(AuthenticationForm):
    # solo cambiamos labels / clases si quieres
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email", "role", "is_active", "is_staff", "is_superuser")