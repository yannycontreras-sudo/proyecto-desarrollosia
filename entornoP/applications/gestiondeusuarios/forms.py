from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Avatar


User = get_user_model()


class RegistroForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()

        if not email:
            raise ValidationError("Este campo es obligatorio.")

        try:
            _, domain = email.split("@", 1)
        except ValueError:
            raise ValidationError("Correo electrónico inválido.")

        # Dominios permitidos
        allowed_domains = (
            "ucn.cl",
            "alumnos.ucn.cl",
            "gmail.com",
            "hotmail.cl",
            "hotmail.com",
            "outlook.com",
        )

        if domain not in allowed_domains:
            raise ValidationError("Dominio no permitido. Usa correo institucional UCN o Gmail/Hotmail si eres administrador.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data.get("email", "").lower()

        # 🔥 Asignación automática de rol según el correo
        if email.endswith("@alumnos.ucn.cl"):
            user.role = "alumno"

        elif email.endswith("@ucn.cl"):
            user.role = "teacher"

        elif email.endswith("@gmail.com") or email.endswith("@hotmail.cl") or email.endswith("@hotmail.com") or email.endswith("@outlook.com"):
            user.role = "admin"
            user.is_staff = True
            user.is_superuser = True

        else:
            user.role = "alumno"   # fallback opcional

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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "telefono",
            "direccion",
            "nombre_emergencia",
            "telefono_emergencia",
            "photo",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_emergencia": forms.TextInput(attrs={"class": "form-control"}),
            "telefono_emergencia": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.FileInput(attrs={"class":"form-control"}),
        }



class AvatarSelectionForm(forms.ModelForm):
    avatar = forms.ModelChoiceField(
        queryset=Avatar.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Selecciona tu avatar"
    )

    class Meta:
        model = User
        fields = ["avatar"]
