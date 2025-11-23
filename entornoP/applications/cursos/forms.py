from django import forms
from .models import Curso, Modulo


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ["nombre", "descripcion"]
        # si quisieras que el docente pueda agregar otros docentes:
        # fields = ["nombre", "descripcion", "docentes"]

class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = ["titulo", "descripcion", "orden"]