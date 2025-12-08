from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Avatar   # 👈 importamos también Avatar


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # Qué columnas mostrar en la tabla de usuarios
    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")

    # Organización de las secciones dentro del formulario de usuario
    fieldsets = (
        ("General", {
            "fields": ("username", "password", "role"),
        }),
        ("Información personal", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "telefono",
                "direccion",
                "nombre_emergencia",
                "telefono_emergencia",
                "photo",
                "avatar",        # 👈 avatar elegido para simulaciones
            ),
        }),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Fechas importantes", {
            "fields": ("last_login", "date_joined"),
        }),
    )

    # Formulario para agregar usuarios desde el admin
    add_fieldsets = (
        ("General", {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2"),
        }),
    )


# 👉 Admin para la librería de avatares
@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
