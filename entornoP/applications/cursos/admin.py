from django.contrib import admin
from django.contrib.auth.admin import UserAdmin




from .models import (
    User,
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
    RecursoMultimedia
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

@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo")
    search_fields = ("titulo",)


@admin.register(RecursoMultimedia)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "tipo", "modulo", "creador", "fecha_subida")
    list_filter = ("tipo", "modulo")
    search_fields = ("titulo",)


admin.site.register(Simulacion)
admin.site.register(Contenido)
admin.site.register(Examen)
admin.site.register(Formulario)
admin.site.register(Evaluacion)
admin.site.register(Pregunta)
admin.site.register(OpcionRespuesta)
admin.site.register(RespuestaAlumno)



