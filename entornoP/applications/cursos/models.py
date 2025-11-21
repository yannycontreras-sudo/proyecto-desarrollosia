# applications/cursos/models.py
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Curso(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)

    # opcional: docentes asignados al curso
    docentes = models.ManyToManyField(
        User,
        blank=True,
        related_name="cursos_dictados",
        limit_choices_to={"role": "teacher"},
    )

    def __str__(self):
        return self.nombre


class Inscripcion(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inscripciones",
        limit_choices_to={"role": "student"},
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="inscripciones",
    )
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "curso")

    def __str__(self):
        return f"{self.usuario} en {self.curso}"


class Modulo(models.Model):
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="modulos",
    )
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["curso", "orden"]

    def __str__(self):
        return f"{self.curso} - {self.titulo}"


class Simulacion(models.Model):
    # 1 módulo -> 1 simulación (1:1)
    modulo = models.OneToOneField(
        Modulo,
        on_delete=models.CASCADE,
        related_name="simulacion",
    )
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Contenido(models.Model):
    # 1 módulo -> N contenidos (1:N)
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name="contenidos",
    )
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)

    # opcional: tipo de contenido (video, pdf, quiz introductorio, etc.)
    # tipo = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.titulo


class Examen(models.Model):
    # relación N:1 (varios exámenes pueden asociarse al mismo contenido)
    contenido = models.ForeignKey(
        Contenido,
        on_delete=models.CASCADE,
        related_name="examenes",
    )
    titulo = models.CharField(max_length=255)
    fecha = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.titulo


class Formulario(models.Model):
    """
    Representa el 'bloque de preguntas' que responde el alumno.
    Según tu diagrama:
      - Contenido 1:N Formulario
      - Simulación 1:1 Formulario
      - Examen 1:1 Formulario
    """

    contenido = models.ForeignKey(
        Contenido,
        on_delete=models.CASCADE,
        related_name="formularios",
    )

    simulacion = models.OneToOneField(
        Simulacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="formulario",
    )

    examen = models.OneToOneField(
        Examen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="formulario",
    )

    instrucciones = models.TextField(blank=True)

    def __str__(self):
        return f"Formulario #{self.pk}"


class Evaluacion(models.Model):
    """
    Intento del alumno sobre un formulario.
    Formulario 1:N Evaluación
    """

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="evaluaciones",
        limit_choices_to={"role": "student"},
    )
    formulario = models.ForeignKey(
        Formulario,
        on_delete=models.CASCADE,
        related_name="evaluaciones",
    )
    fecha = models.DateTimeField(auto_now_add=True)
    puntaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario} - {self.formulario}"


# ========= Preguntas y respuestas del formulario =========

class Pregunta(models.Model):
    """
    Pregunta perteneciente a un formulario (examen/simulación/cuestionario).
    """
    formulario = models.ForeignKey(
        Formulario,
        on_delete=models.CASCADE,
        related_name="preguntas",
    )
    texto = models.TextField()
    orden = models.PositiveIntegerField(default=1)

    # opcional: tipo de pregunta
    # tipo = models.CharField(
    #     max_length=20,
    #     choices=[("single", "Opción única"), ("multi", "Opción múltiple")]
    # )

    class Meta:
        ordering = ["formulario", "orden"]

    def __str__(self):
        return self.texto[:50]


class OpcionRespuesta(models.Model):
    """
    Opción de respuesta para una pregunta de selección.
    """
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="opciones",
    )
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return self.texto


class RespuestaAlumno(models.Model):
    """
    Respuesta del alumno a una pregunta específica dentro de una evaluación.
    """
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name="respuestas",
    )
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion = models.ForeignKey(OpcionRespuesta, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("evaluacion", "pregunta")

    def __str__(self):
        return f"{self.evaluacion} - {self.pregunta_id}"