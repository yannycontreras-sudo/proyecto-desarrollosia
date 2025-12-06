from django.db import models

from django.conf import settings


class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('ABIERTO', 'Abierto'),
        ('EN_PROCESO', 'En proceso'),
        ('CERRADO', 'Cerrado'),
    ]

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default='ABIERTO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.estado}"
