from django.contrib import admin
from .models import (
    Curso,
    Inscripcion,
    Modulo,
    Simulacion,
    Contenido,
    Examen,
    Formulario,
    Evaluacion,
    Pregunta,
    OpcionRespuesta,
    RespuestaAlumno,
)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)
    filter_horizontal = ("docentes",)


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "curso", "fecha_inscripcion")
    list_filter = ("curso",)


admin.site.register(Modulo)
admin.site.register(Simulacion)
admin.site.register(Contenido)
admin.site.register(Examen)
admin.site.register(Formulario)
admin.site.register(Evaluacion)
admin.site.register(Pregunta)
admin.site.register(OpcionRespuesta)
admin.site.register(RespuestaAlumno)