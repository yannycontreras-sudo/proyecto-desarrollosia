from django.db import models

# Create your models here.


from django.db import models



class Administrador(models.Model):
    nombre = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre