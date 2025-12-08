from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ticket(models.Model):
    ESTADOS = [
        ("RECIBIDO", "Recibido"),
        ("EN_REVISION", "En revisión"),
        ("EN_PROGRESO", "En progreso"),
        ("RESUELTO", "Resuelto"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default="RECIBIDO")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
