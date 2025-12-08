from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
# Admin, alumno y docente, class user




class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "alumno", "Alumno"
        TEACHER = "teacher", "Docente"
        ADMIN = "admin", "Administrador"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
        # Campos adicionales del perfil
    telefono = models.CharField("Número de teléfono", max_length=20, blank=True, null=True)
    direccion = models.CharField("Dirección", max_length=255, blank=True, null=True)
    nombre_emergencia = models.CharField("Nombre contacto de emergencia", max_length=100, blank=True, null=True)
    telefono_emergencia = models.CharField("Teléfono contacto de emergencia", max_length=20, blank=True, null=True)


    # si quieres obligar email único, hazlo en settings:
    # ACCOUNT_UNIQUE_EMAIL = True (si usas allauth)
    # o define unique=True en un CustomUser futuro

    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def is_admin_role(self):
        return self.role == self.Role.ADMIN
    
    def save(self, *args, **kwargs):
        if not self.is_superuser:
            if self.is_teacher() or self.is_admin_role():
                self.is_staff = True
            elif self.is_student():
                self.is_staff = False

        super().save(*args, **kwargs)