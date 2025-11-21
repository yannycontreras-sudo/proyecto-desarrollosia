from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")

    # Aquí definimos qué campos salen en cada pestaña
    fieldsets = (
        ("General", {
            "fields": ("username", "password", "role"),  # role en la pestaña General
        }),
        ("Información personal", {
            "fields": ("first_name", "last_name", "email"),
        }),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Fechas importantes", {
            "fields": ("last_login", "date_joined"),
        }),
    )

    add_fieldsets = (
        ("General", {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2"),
        }),
    )