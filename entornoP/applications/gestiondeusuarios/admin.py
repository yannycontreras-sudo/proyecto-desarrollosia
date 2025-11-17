from django.contrib import admin
from .models import *
# Register your models here.


class AdministradorAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'apellido',
        'correo',


    )


admin.site.register(Administrador, AdministradorAdmin)
