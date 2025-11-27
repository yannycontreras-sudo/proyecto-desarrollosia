from django import forms
from django.conf import settings
from django.forms import inlineformset_factory
import os

from .models import (Curso,Modulo,Contenido, Pregunta,OpcionRespuesta,RecursoMultimedia)

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

#Preguntas y opciones de respuesta
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

# Formulario para que el alumno responda preguntas
class ResponderFormularioForm(forms.Form):
    def __int__(self, *args,**kwargs):
        preguntas = kwargs.pop("preguntas")
        super().__init__(*args, **kwargs)

        for pregunta in preguntas:
            field_name = f"pregunta_{pregunta.id}"
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

# Formulario para subir recursos multimedia
class RecursoMultimediaForm(forms.ModelForm):
    class Meta:
        model = RecursoMultimedia
        fields = ["modulo", "titulo", "tipo", "archivo"]

    def clean_archivo(self):
        archivo = self.cleaned_data.get("archivo")
        if not archivo:
            raise forms.ValidationError("Seleccione un archivo.")

        # Validar tamaño (usa settings o 50MB por defecto)
        max_bytes = getattr(settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", 50 * 1024 * 1024)
        if archivo.size > max_bytes:
            mb = max_bytes // (1024 * 1024)
            raise forms.ValidationError(f"Archivo demasiado grande. Máximo permitido: {mb} MB.")

        # Validar extensión
        extensiones_validas = [
            ".jpg", ".jpeg", ".png", ".gif", ".webp",
            ".mp4", ".webm", ".ogg", ".mov",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx",
            ".ppt", ".pptx", ".txt",
        ]

        ext = os.path.splitext(f.name)[1].lower()
        if ext not in extensiones_validas:
            raise forms.ValidationError("Tipo de archivo no permitido.")

        return archivo

class SubirRecursoForm(forms.ModelForm):
    class Meta:
        model = RecursoMultimedia
        fields = ['modulo', 'titulo', 'tipo', 'archivo']
