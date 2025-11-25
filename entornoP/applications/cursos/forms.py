from django import forms
from .models import Curso, Modulo, Contenido


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

class ContenidoForm(forms.ModelForm):
    class Meta:
        model = Contenido
        fields = ["titulo", "descripcion", "archivo"]


from .models import Pregunta, OpcionRespuesta
from django.forms import inlineformset_factory

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ["texto" , "orden"]

class OpcionRespuestaForm(forms.ModelForm):
    class Meta:
        model = OpcionRespuesta
        fields = ["texto" , "es_correcta"]

OpcionRespuestaFormSet = inlineformset_factory(
    Pregunta,
    OpcionRespuesta,
    form=OpcionRespuestaForm,
    extra = 4,
    can_delete = False
)