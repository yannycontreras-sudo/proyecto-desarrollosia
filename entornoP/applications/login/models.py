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


class Reporte(models.Model):
    nombre = models.CharField('Nombre del reporte', max_length=100)
    fecha_generacion = models.DateField('Fecha de generación del reporte')
    contenido_extraido = models.TextField('Contenido')

    def __str__(self):
        return f"Reporte {self.id}: {self.nombre}"

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"


class Simulacion(models.Model):
    nombre = models.CharField('Nombre de la simulación', max_length=300)
    fecha_inicio = models.DateField('Fecha de inicio de la simulación')
    fecha_fin = models.DateField('Fecha de término de la simulación')
    motivo_consulta = models.CharField('Motivo de la consulta', max_length=300)
    nombre_estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.nombre}"

    class Meta:
        verbose_name = "Simulación"
        verbose_name_plural = "Simulaciones"


class Diagnostico(models.Model):
    hipotesis = models.CharField(
        'Posible diagnóstico o idea inicial sobre el caso', max_length=300)
    justificacion = models.CharField(
        'Justificación del diagnóstico', max_length=300)
    fecha_envio = models.DateField('Fecha de envío del diagnóstico')
    estado = models.CharField('Estado del diagnóstico', max_length=150)

    def __str__(self):
        return f"Diagnóstico {self.id} - {self.estado}"

    class Meta:
        verbose_name = "Diagnóstico"
        verbose_name_plural = "Diagnósticos"


class ExamenFisico(models.Model):
    fecha_registro = models.DateField('Fecha de registro')
    fecha_examen = models.DateField('Fecha del examen físico')
    hallazgos = models.CharField(
        'Hallazgos en el examen físico', max_length=300)

    def __str__(self):
        return f"Examen físico {self.id}"

    class Meta:
        verbose_name = "Examen físico"
        verbose_name_plural = "Exámenes físicos"


class CasoClinico(models.Model):
    titulo = models.CharField('Nombre del caso clínico', max_length=300)
    resumen = models.CharField('Resumen del caso clínico', max_length=300)
    estado = models.CharField('Estado del caso', max_length=300)

    def __str__(self):
        return f"{self.id} - {self.titulo}"

    class Meta:
        verbose_name = "Caso clínico"
        verbose_name_plural = "Casos clínicos"


class ContenidoMultimedia(models.Model):
    tipo = models.CharField('Tipo de contenido', max_length=300)
    url_contenido = models.URLField('URL del contenido')
    descripcion = models.CharField('Descripción', max_length=300)

    def __str__(self):
        return f"Contenido {self.id} - {self.tipo}"

    class Meta:
        verbose_name = "Contenido multimedia"
        verbose_name_plural = "Contenidos multimedia"


class PlanDeTratamiento(models.Model):
    objetivo = models.CharField(
        'Objetivo del plan de tratamiento', max_length=300)
    detalle = models.CharField('Detalle del plan', max_length=300)
    fecha_envio = models.DateField('Fecha de envío del plan de tratamiento')
    estado = models.CharField('Estado del plan de tratamiento', max_length=300)

    def __str__(self):
        return f"Plan de tratamiento {self.id}"

    class Meta:
        verbose_name = "Plan de tratamiento"
        verbose_name_plural = "Planes de tratamiento"


class Paciente(models.Model):
    nombre = models.CharField('Nombre del paciente', max_length=100)
    apellido = models.CharField('Apellido del paciente', max_length=100)
    correo = models.CharField('Correo del paciente', max_length=200)

    def __str__(self):
        return f"{self.id} - {self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
