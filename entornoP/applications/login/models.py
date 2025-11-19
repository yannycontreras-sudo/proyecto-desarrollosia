from django.db import models

# Create your models here.


from django.db import models


class Estudiante(models.Model):
    nombre = models.CharField('Nombre del estudiante', max_length=150)
    apellido = models.CharField('Apellido del estudiante', max_length=150)
    correo = models.CharField('Correo del estudiante', max_length=200)

    def __str__(self):
        return f"{self.id} - {self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"


class Evaluacion(models.Model):
    calificacion = models.FloatField('Calificación')
    retroalimentacion = models.CharField('Retroalimentación', max_length=500)
    fecha_evaluacion = models.DateField('Fecha de la evaluación')

    def __str__(self):
        return f"Evaluación {self.id} - {self.fecha_evaluacion}"

    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"


class ContenidoMultimedia(models.Model):
    tipo = models.CharField('Tipo de contenido', max_length=300)
    url_contenido = models.URLField('URL del contenido')
    descripcion = models.CharField('Descripción', max_length=300)

    def __str__(self):
        return f"Contenido {self.id} - {self.tipo}"

    class Meta:
        verbose_name = "Contenido multimedia"
        verbose_name_plural = "Contenidos multimedia"

