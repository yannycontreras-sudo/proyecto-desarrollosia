from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model



User = get_user_model()


class RegistroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # 👇 ya NO ponemos "role" aquí
        fields = ("username", "email")

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

    def save(self, commit=True):
        # llamamos a UserCreationForm.save() pero SIN guardar todavía
        user = super().save(commit=False)
        # 👇 rol fijo para todos los que se registran por el front
        user.role = "student"   # o el valor que uses internamente para "Alumno"
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    # solo cambiamos labels / clases si quieres
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def confirm_login_allowed(self, user):
        email = (user.email or "").strip().lower()

        if not email:
            raise ValidationError(
                "Tu cuenta no tiene un correo asociado.",
                code="no_email",
            )
        
        try:
            _, domain = email.split("@", 1)
        except ValueError:
            raise ValidationError(
                "Correo electronico invalido.",
                code="invalid_email",
            )
        
        allowed_domains = ("ucn.cl", "alumnos.ucn.cl")

        if domain not in allowed_domains:
            raise ValidationError(
                "Solo se permite iniciar sesión con correos institucionales"
                "(@ucn.cl o @alumnos.ucn.cl).",
                code="invalid_domains",
            )


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email", "role", "is_active", "is_staff", "is_superuser")