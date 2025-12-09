# applications/cursos/models.py
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL


# ============================================================
# CURSOS E INSCRIPCIONES
# ============================================================

class Curso(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)

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


# ============================================================
# MÓDULOS, CONTENIDOS, SIMULACIONES, EXÁMENES
# ============================================================

class Modulo(models.Model):
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name="modulos")
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=1)

    publicado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.curso.nombre} - {self.titulo}"


class Simulacion(models.Model):
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
    modulo = models.ForeignKey(
        Modulo, on_delete=models.CASCADE, related_name="contenidos")
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to="contenidos/", null=True, blank=True)

    def __str__(self):
        return self.titulo

    @property
    def es_video(self):
        nombre = (self.archivo.name or "").lower()
        return nombre.endswith((".mp4", ".webm", ".ogg"))

    @property
    def es_imagen(self):
        nombre = (self.archivo.name or "").lower()
        return nombre.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))


class Examen(models.Model):
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


# ============================================================
# PREGUNTAS Y RESPUESTAS
# ============================================================

class Pregunta(models.Model):
    TIPO_SELECCION = "seleccion"
    TIPO_ABIERTA = "abierta"

    TIPO_CHOICES = [
        (TIPO_SELECCION, "Selección múltiple"),
        (TIPO_ABIERTA, "Pregunta abierta"),
    ]

    formulario = models.ForeignKey(
        Formulario,
        on_delete=models.CASCADE,
        related_name="preguntas",
    )
    texto = models.TextField()
    orden = models.PositiveIntegerField(default=1)
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=TIPO_SELECCION,
    )

    respuesta_esperada = models.TextField(
        blank=True,
        help_text="Solo se usa si la pregunta es abierta.",
    )

    class Meta:
        ordering = ["formulario", "orden"]

    def __str__(self):
        return self.texto[:50]


class OpcionRespuesta(models.Model):
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
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name="respuestas",
    )
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion = models.ForeignKey(
        OpcionRespuesta,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    respuesta_texto = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("evaluacion", "pregunta")

    def __str__(self):
        return f"{self.evaluacion} - {self.pregunta_id}"


# ============================================================
# PROGRESO DEL MÓDULO
# ============================================================

class ProgresoModulo(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("en_progreso", "En progreso"),
        ("completado", "Completado"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="progresos_modulos",
        limit_choices_to={"role": "student"},
    )

    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name="progresos",
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="pendiente",
    )

    progreso = models.PositiveIntegerField(default=0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("usuario", "modulo")

    def save(self, *args, **kwargs):
        if self.progreso >= 100:
            self.estado = "completado"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} - {self.modulo} ({self.estado})"


# ============================================================
# FUNCIONES AUTOMÁTICAS
# ============================================================

def marcar_modulo_completado(usuario, modulo):
    progreso, _ = ProgresoModulo.objects.get_or_create(
        usuario=usuario,
        modulo=modulo
    )
    progreso.progreso = 100
    progreso.estado = "completado"
    progreso.save()


def desbloquear_siguiente_modulo(modulo, usuario):
    curso = modulo.curso
    modulos = list(curso.modulos.order_by("orden"))

    if modulo in modulos:
        idx = modulos.index(modulo)
        if idx + 1 < len(modulos):
            siguiente = modulos[idx + 1]
            ProgresoModulo.objects.get_or_create(
                usuario=usuario,
                modulo=siguiente
            )


# ============================================================
# SEÑAL DE APROBACIÓN DE EVALUACIÓN (CORREGIDA)
# ============================================================

@receiver(post_save, sender=Evaluacion)
def evaluar_modulo(sender, instance, created, **kwargs):
    """
    Cuando el alumno aprueba una Evaluacion se marca el módulo como completado
    y se desbloquea el siguiente módulo.
    """

    # Si no está aprobado ⇒ no hacemos nada
    if not instance.aprobado:
        return

    formulario = instance.formulario

    # El formulario SIEMPRE debe tener contenido. Si no, no se puede avanzar.
    contenido = getattr(formulario, "contenido", None)
    if contenido is None:
        return

    modulo = contenido.modulo
    usuario = instance.usuario

    # Marca módulo como completado
    marcar_modulo_completado(usuario, modulo)

    # Desbloquea el siguiente módulo
    desbloquear_siguiente_modulo(modulo, usuario)

class ProgresoSimulacion(models.Model):
    ESTADOS = [
        ("iniciada", "Iniciada"),
        ("completada", "Completada"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    simulacion = models.ForeignKey(Simulacion, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="iniciada")

    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    @property
    def tiempo_total(self):
        if self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).total_seconds()
        return None

    def __str__(self):
        return f"{self.usuario} - {self.simulacion} ({self.estado})"
