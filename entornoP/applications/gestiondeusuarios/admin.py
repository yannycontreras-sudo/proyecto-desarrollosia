from django.contrib import admin
from .models import *
# Register your models here.


class Administrador(admin.ModelAdmin):
    list_display = ('user', 'rut', 'cargo', 'telefono', 'fecha_creacion'),
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'rut', 'cargo'),




