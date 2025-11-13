from django.db import models
from applications.login.models import Estudiante
# Create your models here.


class Administrador(models.Model):
    nombre = models.CharField(
        'Nombre del administrador', max_length=150, null=False)
    apellido = models.CharField(
        'Apellido del administrador', max_length=150, null=False)
    correo = models.CharField(
        'Correo del administrador', max_length=150, null=False)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + " " + self.nombre + " " + self.apellido

    class Meta:
        verbose_name_plural = "Administradores"
