from django import forms
from .models import Curso, Modulo, Contenido, Pregunta, OpcionRespuesta, Formulario


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
        fields = ["texto" , "orden", "tipo"]

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

from .models import Pregunta, OpcionRespuesta
from django import forms

class ResponderFormularioForm(forms.Form):
    """
    Crea dinamicamente un campo por cada pregunta del formulario.
    - Si la pregunta es de seleccion multiple --> ChoiceField con radios.
    -Si la prefunta es abierta --> CharField con Textarea
    """
    def __int__(self, *args,**kwargs):
        preguntas = kwargs.pop("preguntas")
        super().__init__(*args, **kwargs)

        for pregunta in preguntas:
            field_name = f"pregunta_{pregunta.id}"

            if pregunta.tipo == Pregunta.TIPO_ABIERTA:
                self.fields[field_name] = forms.CharField(
                    label = pregunta.texto,
                    widget = forms.Textarea(attrs={"rows": 3}),
                    required = False,
                )
            else:
                choices = [
                (opcion.id, opcion.texto)
                for opcion in pregunta.opciones.all()
            ]
            self.fields[field_name] = forms.ChoiceField(
                label=pregunta.texto,
                choices=choices,
                widget=forms.RadioSelect,
                required = True,
            )

from django.forms import formset_factory
from .models import Pregunta, OpcionRespuesta


class PreguntaConOpcionesForm(forms.Form):
    """
    Un formulario que representa UNA pregunta del formulario,
    con sus posibles opciones (si es de selección múltiple).
    """
    texto = forms.CharField(
        label="Texto de la pregunta",
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    orden = forms.IntegerField(label="Orden", initial=1)

    # usamos los choices definidos en el modelo Pregunta
    tipo = forms.ChoiceField(
        label="Tipo de pregunta",
        choices=Pregunta.TIPO_CHOICES,
        initial=Pregunta.TIPO_SELECCION,
    )

    # Hasta 4 opciones (puedes subir o bajar la cantidad)
    opcion_1 = forms.CharField(label="Opción 1", required=False)
    correcta_1 = forms.BooleanField(label="Correcta", required=False)

    opcion_2 = forms.CharField(label="Opción 2", required=False)
    correcta_2 = forms.BooleanField(label="Correcta", required=False)

    opcion_3 = forms.CharField(label="Opción 3", required=False)
    correcta_3 = forms.BooleanField(label="Correcta", required=False)

    opcion_4 = forms.CharField(label="Opción 4", required=False)
    correcta_4 = forms.BooleanField(label="Correcta", required=False)


# Formset: varias preguntas en una sola página
PreguntaConOpcionesFormSet = formset_factory(
    PreguntaConOpcionesForm,
    extra=3,        # cuántas preguntas vacías aparecen por defecto
    can_delete=True # permite marcar para borrar preguntas
)

class ResponderFormularioForm(forms.Form):
    """
    Formulario dinamico para que el alumno responda en Formulario
    Crea un campo por cada pregunta:
    -Seleccion Multiple ChoiceField con RadioSelect
    -Abierta CharField co Texttarea
    """
    def __init__(self, *args, preguntas = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.preguntas = preguntas or []

        for pregunta in self.preguntas:
            field_name = f"preguntas_{pregunta.id}"

            #preguta abierta 

            if pregunta.tipo == Pregunta.TIPO_ABIERTA:
                self.fields[field_name] = forms.ChField(
                    label = pregunta.texto,
                    widget = forms.Textarea(
                        attrs={
                            "rows": 3,
                            "class": "form-control",
                            "placeholder": "Escribe tu respuesta...",
                        }
                    ),
                    requiered = True
                )

                    #pregunta dde seleccion multiple

            else:
                opciones =[
                    (op.id, op.texto)
                    for op in pregunta.opciones.all()
                ]
                self.fields[field_name] = forms.ChoiceField(
                    label = pregunta.texto,
                    choices=opciones,
                    widget=forms.RadioSelect,
                    required = True,
                )
                
class FormularioForm(forms.ModelForm):
    class Meta:
        model = Formulario
        fields ={"instrucciones"}

