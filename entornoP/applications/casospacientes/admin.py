from django.contrib import admin

# Register your models here.

<<<<<<< Updated upstream


class CasoClinicoAdmin(admin.ModelAdmin):
    list_display = ("id", "paciente", "diagnostico_principal", "fecha")
    search_fields = ("paciente__nombre", "diagnostico_principal")
    list_filter = ("fecha",)
=======
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre", "edad")
    search_fields = ("rut", "nombre")
    list_filter = ("edad",)
    ordering = ("nombre",)
>>>>>>> Stashed changes
