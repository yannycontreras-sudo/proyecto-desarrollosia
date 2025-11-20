from django.db import models

# Create your models here.
# Admin, alumno y docente, class user




class Administrador(models.Model):
    nombre = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre