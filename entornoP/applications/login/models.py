from django.db import models

# Create your models here.


class Estudiante(models.Model):
    nombre = models.CharField('Nombre del estudiante',
                              max_length=150, null=False)
    apellido = models.CharField(
        'Apellido del estudiante', max_length=150, null=False)
    correo = models.CharField('Correo del estudiante',
                              max_length=200, null=False)

    def __str__(self):
        return str(self.id)+'-'+self.nombre


class Evaluaciones(models.Model):
    calificacion = models.FloatField(
        'Calificación', max_length=100, null=False)
    retroalimentacion = models.CharField('Retroalimentación', null=False)
    fecha_evaluacion = models.DateField('Fecha de la evaluación')

    def __str__(self):
        return self


class Reporte(models.Model):
    nombre = models.CharField('Nombre del reporte', max_length=100, null=False)
    fecha_generacion = models.DateField('Fecha de generación del reporte')
    contenido_extraido = models.CharField('Contenido', null=False)

    def __str__(self):
        return super().__str__()


class Simulacion(models.Model):
    nombre = models.CharField(
        'Nombre de la simulación', max_length=300, null=False)
    fecha_inicio = models.DateField('Fecha de inicio de la simulación')
    fecha_fin = models.DateField('Fecha de término de la simulación')
    motivo_consulta = models.CharField(
        'Motivo de la consulta', max_length=300, null=False)
    nombre_estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)+'-'+self.nombre


class Diagnostico(models.Model):
    hipotesis = models.CharField(
        'Posible diagnostico o idea inicial sobre el caso', max_length=300, null=False)
    justificacion = models.CharField(
        'Justificación del diagnóstico', max_length=300, null=False)
    fecha_envio = models.DateField('Fecha de envío del diagnóstico')
    estado = models.CharField('Estado del diagnóstico',
                              max_length=150, null=False)

    def __str__(self):
        return super().__str__()


class Examen_fisico(models.Model):
    fecha_registro = models.DateField('Fecha de registro')
    fecha_examen = models.DateField('Fecha del examen físico')
    hallazgos = models.CharField(
        'Hallazgos en el examen físico', max_length=300, null=False)

    def __str__(self):
        return super().__str__()


class Caso_clinico(models.Model):
    titulo = models.CharField(
        'Nombre del caso clínico', max_length=300, null=False)
    resumen = models.CharField(
        'Resumen del caso clínico', max_length=300, null=False)
    estado = models.CharField('Estado del caso', max_length=300, null=False)

    def __str__(self):
        return super().__str__()


class Contenido_multimedia(models.Model):
    tipo = models.CharField('Tipo de contenido', max_length=300, null=False)
    url_contenido = models.URLField()
    descripcion = models.CharField('Descripción', max_length=300, null=False)

    def __str__(self):
        return super().__str__()


class Plan_de_tratamiento(models.Model):
    objetivo = models.CharField(
        'Objetivo del plan de tratamiento', max_length=300, null=False)
    detalle = models.CharField('Detalle del plan', max_length=300, null=False)
    fecha_envio = models.DateField('Fecha de envío del plan de tratamiento')
    estado = models.CharField(
        'Estado del plan de tratamiento', max_length=300, null=False)

    def __str__(self):
        return super().__str__()


class Paciente(models.Model):
    nombre = models.CharField('Nombre del paciente',
                              max_length=100, null=False)
    apellido = models.CharField(
        'Apellido del paciente', max_length=100, null=False)
    correo = models.CharField('Correo del paciente',
                              max_length=200, null=False)

    def __str__(self):
        return super().__str__()
