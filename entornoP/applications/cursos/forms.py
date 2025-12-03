from django import forms
from django.forms import inlineformset_factory, formset_factory

from .models import (
    Curso,
    Modulo,
    Contenido,
    Pregunta,
    OpcionRespuesta,
    Formulario,
)


# ======================= CURSOS / MÓDULOS / CONTENIDOS =======================

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


# ======================= PREGUNTAS / OPCIONES (MODELO DIRECTO) =======================

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ["texto", "orden", "tipo", "respuesta_esperada"]


class OpcionRespuestaForm(forms.ModelForm):
    class Meta:
        model = OpcionRespuesta
        fields = ["texto", "es_correcta"]


OpcionRespuestaFormSet = inlineformset_factory(
    Pregunta,
    OpcionRespuesta,
    form=OpcionRespuestaForm,
    extra=4,
    can_delete=False,
)


# ======================= FORM “PREGUNTA + OPCIONES” (para el formset de edición) =====

class PreguntaConOpcionesForm(forms.Form):
    """
    Un formulario que representa UNA pregunta del formulario,
    con sus posibles opciones (si es de selección múltiple).
    Lo usamos normalmente dentro de un formset.
    """
    texto = forms.CharField(
        label="Texto de la pregunta",
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
    )
    orden = forms.IntegerField(
        label="Orden",
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    # usamos los choices definidos en el modelo Pregunta
    tipo = forms.ChoiceField(
        label="Tipo de pregunta",
        choices=Pregunta.TIPO_CHOICES,
        initial=Pregunta.TIPO_SELECCION,
        widget=forms.Select(attrs={"class": "form-control tipo-pregunta-select"}),
    )

    # 👉 NUEVO: respuesta esperada SOLO para pregunta abierta
    respuesta_esperada = forms.CharField(
        label="Respuesta esperada (solo pregunta abierta)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "class": "form-control",
                "placeholder": "Escribe aquí la respuesta modelo para una pregunta abierta...",
            }
        ),
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


# ======================= FORMULARIO PARA RESPONDER (ALUMNO) =======================

class ResponderFormularioForm(forms.Form):
    """
    Formulario dinámico para que el alumno responda un Formulario.
    Crea un campo por cada pregunta:
      - Pregunta de selección múltiple -> ChoiceField con RadioSelect
      - Pregunta abierta -> CharField con Textarea
    """

    def __init__(self, *args, preguntas=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.preguntas = preguntas or []

        for pregunta in self.preguntas:
            field_name = f"pregunta_{pregunta.id}"

            # Pregunta abierta
            if pregunta.tipo == Pregunta.TIPO_ABIERTA:
                self.fields[field_name] = forms.CharField(
                    label=pregunta.texto,
                    widget=forms.Textarea(
                        attrs={
                            "rows": 3,
                            "class": "form-control",
                            "placeholder": "Escribe tu respuesta...",
                        }
                    ),
                    required=True,
                )
            else:
                # Selección múltiple
                opciones = [
                    (op.id, op.texto)
                    for op in pregunta.opciones.all()
                ]
                self.fields[field_name] = forms.ChoiceField(
                    label=pregunta.texto,
                    choices=opciones,
                    widget=forms.RadioSelect,
                    required=True,
                )


# ======================= FORMULARIO (MODELO) =======================

class FormularioForm(forms.ModelForm):
    class Meta:
        model = Formulario
        fields = ["instrucciones"]
