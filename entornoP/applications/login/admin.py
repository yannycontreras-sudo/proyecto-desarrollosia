from django.contrib import admin
from .models import *
# Register your models here.


class EstudianteAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'apellido',
        'correo',


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





admin.site.register(Estudiante, EstudianteAdmin)
admin.site.register(ContenidoMultimedia, ContenidoMultimediaAdmin)

