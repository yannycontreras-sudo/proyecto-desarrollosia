from django.contrib import admin
from .models import *
# Register your models here.


class EstudianteAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'apellido',
        'correo',


    )


class EvaluacionAdmin(admin.ModelAdmin):
    list_display = (
        'calificacion',
        'retroalimentacion',
        'fecha_evaluacion',


    )


class ReporteAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'fecha_generacion',
        'contenido_extraido',


    )


class SimulacionAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'fecha_inicio',
        'fecha_fin',
        'motivo_consulta',
        'nombre_estudiante',


    )


class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = (
        'hipotesis',
        'justificacion',
        'fecha_envio',
        'estado',


    )


class ExamenFisicoAdmin(admin.ModelAdmin):
    list_display = (
        'fecha_registro',
        'fecha_examen',
        'hallazgos',


    )


class CasoClinicoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'resumen',
        'estado',


    )


class ContenidoMultimediaAdmin(admin.ModelAdmin):
    list_display = (
        'tipo',
        'url_contenido',
        'descripcion',


    )


class PlanDeTratamientoAdmin(admin.ModelAdmin):
    list_display = (
        'objetivo',
        'detalle',
        'fecha_envio',
        'estado',


    )


class AdministradorAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'apellido',
        'correo',


    )


class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'apellido',
        'correo',


    )


admin.site.register(Estudiante, EstudianteAdmin)
admin.site.register(Evaluacion, EvaluacionAdmin)
admin.site.register(ContenidoMultimedia, ContenidoMultimediaAdmin)

