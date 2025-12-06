from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User   # 👈 tu modelo personalizado


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # Qué columnas mostrar en la tabla
    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")

    # Organización de las pestañas dentro del admin
    fieldsets = (
        ("General", {
            "fields": ("username", "password", "role"),
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

    # Formulario para agregar usuarios (sin CustomUserCreationForm)
    add_fieldsets = (
        ("General", {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2"),
        }),
    )
