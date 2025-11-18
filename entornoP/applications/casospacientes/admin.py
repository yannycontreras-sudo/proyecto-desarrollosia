from django.contrib import admin

# Register your models here.



class CasoClinicoAdmin(admin.ModelAdmin):
    list_display = ("id", "paciente", "diagnostico_principal", "fecha")
    search_fields = ("paciente__nombre", "diagnostico_principal")
    list_filter = ("fecha",)