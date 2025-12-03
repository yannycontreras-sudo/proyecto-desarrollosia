from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from difflib import SequenceMatcher


from .forms import (
    CursoForm,
    ModuloForm,
    ContenidoForm,
    PreguntaForm,
    OpcionRespuestaFormSet,
    ResponderFormularioForm,
    PreguntaConOpcionesFormSet,
    FormularioForm,
)

from .models import (
    Curso,
    Modulo,
    Contenido,
    Formulario, 
    Pregunta,
    Evaluacion,
    OpcionRespuesta,
    RespuestaAlumno,
    Inscripcion,
    ProgresoModulo,
    )


from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status






# CURSOS


@method_decorator(login_required, name="dispatch")
class CursoListView(ListView):
    model = Curso
    template_name = "cursos/curso_list.html"
    context_object_name = "cursos"


@method_decorator(login_required, name="dispatch")
class CursoDetailView(DetailView):
    model = Curso
    template_name = "cursos/curso_detail.html"
    context_object_name = "curso"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curso = self.object
        user = self.request.user

        # Todos los módulos del curso
        modulos = (
            Modulo.objects
            .filter(curso=curso)
            .order_by("orden")
            .prefetch_related("contenidos")
        )

        # 👇 Si es alumno (role == "student"), solo ve módulos publicados
        # Docentes/admin/superuser ven todos
        if getattr(user, "role", None) == "student" and not user.is_superuser:
            modulos = modulos.filter(publicado=True)

        context["modulos"] = modulos
        context["esta_inscrito"] = Inscripcion.objects.filter(
            usuario=user,
            curso=curso
        ).exists()

        return context


@login_required
def mis_cursos_view(request):
    inscripciones = (
        Inscripcion.objects
        .filter(usuario=request.user)
        .select_related("curso")
    )
    cursos = [i.curso for i in inscripciones]
    return render(request, "cursos/mis_cursos.html", {"cursos": cursos})


@login_required
def inscribirse_curso_view(request, pk):
    curso = get_object_or_404(Curso, pk=pk)

    if request.method == "POST":
        inscripcion, creada = Inscripcion.objects.get_or_create(
            usuario=request.user,
            curso=curso,
        )
        if creada:
            messages.success(
                request, f"Te has inscrito en el curso: {curso.nombre}")
        else:
            messages.info(
                request, f"Ya estabas inscrito en el curso: {curso.nombre}")

        return redirect("cursos:detalle", pk=curso.pk)

    return redirect("cursos:detalle", pk=curso.pk)


class CursoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Curso
    form_class = CursoForm
    template_name = "cursos/curso_form.html"

    # 👇 QUIÉN PUEDE CREAR CURSOS
    def test_func(self):
        user = self.request.user
        # solo docentes, admins o superusuarios
        return getattr(user, "role", None) in ("teacher", "admin") or user.is_superuser

    def form_valid(self, form):
        response = super().form_valid(form)  # aquí se guarda el curso
        messages.success(
            self.request,
            f"Curso creado correctamente. ID del curso: {self.object.id}",
        )
        return response

    def get_success_url(self):
        return reverse_lazy("cursos:detalle", kwargs={"pk": self.object.pk})


class CursoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = "cursos/curso_form.html"
    success_url = reverse_lazy("cursos:lista")

    def test_func(self):
        user = self.request.user
        curso = self.get_object()
        # si quieres exigir que sea docente del curso:
        # es_docente = curso.docentes.filter(pk=user.pk).exists()
        # return es_docente or user.is_superuser
        return getattr(user, "role", None) in ("teacher", "admin") or user.is_superuser

    ##############################################################
    ##############################################################
    # MODULOS


class ModuloCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Modulo
    form_class = ModuloForm
    template_name = "cursos/modulo_form.html"

    def test_func(self):
        user = self.request.user
        return getattr(user, "role", None) in ("teacher", "admin") or user.is_superuser

    def form_valid(self, form):
        curso = get_object_or_404(Curso, pk=self.kwargs["curso_pk"])
        form.instance.curso = curso
        messages.success(self.request, "Módulo creado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("cursos:detalle", kwargs={"pk": self.object.curso.pk})


class ModuloUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Modulo
    form_class = ModuloForm
    template_name = "cursos/modulo_form.html"

    def test_func(self):
        user = self.request.user
        modulo = self.get_object()
        curso = modulo.curso
        return getattr(user, "role", None) in ("teacher", "admin") or user.is_superuser

    def get_success_url(self):
        return reverse_lazy("cursos:detalle", kwargs={"pk": self.object.curso.pk})


@login_required
def modulo_toggle_publicacion_view(request, pk):
    modulo = get_object_or_404(Modulo, pk=pk)
    user = request.user

    # solo teacher / admin / superuser pueden cambiar esto
    if getattr(user, "role", None) not in ("teacher", "admin") and not user.is_superuser:
        messages.error(
            request, "No tienes permiso para cambiar la publicación de este módulo.")
        return redirect("cursos:detalle", pk=modulo.curso.pk)

    # alternar True/False
    modulo.publicado = not modulo.publicado
    modulo.save()

    if modulo.publicado:
        messages.success(
            request, f"El módulo «{modulo.titulo}» ahora está PUBLICADO.")
    else:
        messages.info(
            request, f"El módulo «{modulo.titulo}» ahora está OCULTO.")

    return redirect("cursos:detalle", pk=modulo.curso.pk)

    ##############################################################
    ##############################################################
    # CONTENIDOS


class ContenidoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Contenido
    form_class = ContenidoForm
    template_name = "cursos/contenido_form.html"

    def test_func(self):
        user = self.request.user
        return getattr(user, "role", None) in ("teacher", "admin") or user.is_superuser

    def form_valid(self, form):
        modulo = get_object_or_404(Modulo, pk=self.kwargs["modulo_pk"])
        form.instance.modulo = modulo
        messages.success(self.request, "Contenido creado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("cursos:detalle", kwargs={"pk": self.object.modulo.curso.pk})


class ContenidoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Contenido
    form_class = ContenidoForm
    template_name = "cursos/contenido_form.html"

    def test_func(self):
        user = self.request.user
        # podrías chequear también si es docente del curso
        return getattr(user, "role", None) in ("teacher", "admin") or user.is_superuser

    def get_success_url(self):
        return reverse_lazy("cursos:detalle", kwargs={"pk": self.object.modulo.curso.pk})


class FormularioDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Formulario
    template_name = "cursos/formulario_detalle.html"
    context_object_name = "formulario"

    def test_func(self):
        user = self.request.user
        # solo docentes, admin o superuser
        return getattr(user, "role", None) in ("teacher", "admin") or user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formulario = self.object

        preguntas = (
            Pregunta.objects
            .filter(formulario=formulario)
            .prefetch_related("opciones")
            .order_by("orden")
        )
        context["preguntas"] = preguntas
        return context




# ======================================
# EDITAR VARIAS PREGUNTAS DEL FORMULARIO
# ======================================
    
@login_required
def editar_preguntas_formulario(request, formulario_id):
    """
    Pantalla donde el docente puede crear/editar varias preguntas
    del formulario a la vez (selección múltiple + abiertas).
    """
    formulario = get_object_or_404(Formulario, id=formulario_id)

    user = request.user
    if getattr(user, "role", None) not in ("teacher", "admin") and not user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para editar preguntas.")

    if request.method == "POST":
        formset = PreguntaConOpcionesFormSet(request.POST)

        if formset.is_valid():
            # Borramos preguntas anteriores para simplificar la lógica
            Pregunta.objects.filter(formulario=formulario).delete()

            for form in formset:
                # forms marcados para borrar o totalmente vacíos se saltan
                if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                    continue

                texto = (form.cleaned_data.get("texto") or "").strip()
                if not texto:
                    continue

                orden = form.cleaned_data.get("orden") or 1
                tipo = form.cleaned_data.get("tipo")
                respuesta_esperada = (form.cleaned_data.get("respuesta_esperada") or "").strip()

                # Creamos la pregunta
                pregunta = Pregunta.objects.create(
                    formulario=formulario,
                    texto=texto,
                    orden=orden,
                    tipo=tipo,
                    respuesta_esperada=respuesta_esperada if tipo == Pregunta.TIPO_ABIERTA else "",
                )

                # Si es selección múltiple, creamos las opciones
                if tipo == Pregunta.TIPO_SELECCION:
                    opciones = []
                    for i in range(1, 5):
                        op_text = (form.cleaned_data.get(f"opcion_{i}") or "").strip()
                        es_corr = form.cleaned_data.get(f"correcta_{i}", False)
                        if op_text:
                            opciones.append((op_text, es_corr))

                    if opciones:
                        # Si ninguna está marcada como correcta, marcamos la 1ª
                        if not any(es_corr for _, es_corr in opciones):
                            txt0, _ = opciones[0]
                            opciones[0] = (txt0, True)

                        for op_text, es_corr in opciones:
                            OpcionRespuesta.objects.create(
                                pregunta=pregunta,
                                texto=op_text,
                                es_correcta=es_corr,
                            )

            messages.success(request, "Preguntas del formulario actualizadas correctamente.")
            return redirect("cursos:detalle_formulario", formulario.id)

    else:
        # Cargar preguntas existentes en el formset
        inicial = []
        for p in formulario.preguntas.all().order_by("orden"):
            data = {
                "texto": p.texto,
                "orden": p.orden,
                "tipo": p.tipo,
                "respuesta_esperada": p.respuesta_esperada or "",
            }
            opciones = list(p.opciones.all())
            for i, op in enumerate(opciones[:4], start=1):
                data[f"opcion_{i}"] = op.texto
                data[f"correcta_{i}"] = op.es_correcta
            inicial.append(data)

        if inicial:
            formset = PreguntaConOpcionesFormSet(initial=inicial)
        else:
            formset = PreguntaConOpcionesFormSet()

    return render(
        request,
        "cursos/editar_preguntas_formulario.html",
        {
            "formulario": formulario,
            "formset": formset,
        },
    )



# preguntas


@login_required
def crear_pregunta(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)

    if hasattr(request.user, "is_teacher") and not request.user.is_teacher():
        return HttpResponseForbidden("No tienes permiso para crear preguntas.")

    pregunta = Pregunta(formulario=formulario)

    if request.method == "POST":
        pregunta_form = PreguntaForm(request.POST, instance=pregunta)
        formset = OpcionRespuestaFormSet(request.POST, instance=pregunta)

        if pregunta_form.is_valid() and formset.is_valid():
            pregunta_form.save()

            opciones = formset.save(commit=False)

            tiene_correcta = any(o.es_correcta 
                                 for o in opciones)
            if not tiene_correcta:
                formset, forms[0].add_error(
                    "es correcta",
                    "Debes marcar al menos una opcion correcta."
                )
            else:
                for opcion in opciones:
                    opcion.save()

                messages.success(request, "Pregunta creada correctamente.")
                return redirect("detalle_formulario", formulario_id=formulario.id)
    else:
        pregunta_form = PreguntaForm(instance=pregunta)
        formset = OpcionRespuestaFormSet(instance=pregunta)

    return render(
        request,
        "cursis/crear_pregunta.html",
        {
            "formulario": formulario,
            "pregunta_form": pregunta_form,
            "formset": formset,
        }
    )


@login_required
def editar_pregunta(request, pregunta_id):
    pregunta = get_object_or_404(Pregunta, id=pregunta_id)
    formulario = pregunta.formulario
    if hasattr(request.user, "is_teacher") and not request.user.is_teacher() and getattr(reguest.user, "role, None") != "admin":
        return HttpResponseForbidden("No tienes permiso para editar esta pregunta.")
    if request.method == "POST":
        pregunta_form = PreguntaForm(request.POST, instance=pregunta)
        formset = None
        if pregunta.tipo == Pregunta.TIPO_SELECCION:
            formset = OpcionRespuestaFormSet(request.POST, instance=pregunta)
        if pregunta_form.is_valid() and (formset is None or formset.is_valid()):
            pregunta_form.save()
            if formset is not None:
                opciones = formset.save(commit=False)
                for opcion in opciones:
                    opcion.pregunta = pregunta
                    opcion.save()
            messages.success(request, "Pregunta actualizada correctamente.")
            return redirect("cursos: detalle_formulario", pk=formulario.id)
    else:
        pregunta_form = PreguntaForm(instance=pregunta)
        formset = None
        if pregunta.tipo == Pregunta.TIPO_SELECCION:
            formset = OpcionRespuestaFormSet(instance=pregunta)
    return render(
        request,
        "cursos/editar_pregunta.html",
        {
            "formulario": formulario,
            "pregunta": pregunta,
            "pregunta_form": pregunta_form,
            "formset": formset,
        },
    )

    # respuesta del alumnos al formulario


@login_required
def responder_formulario(request, formulario_id):
    formulario = get_object_or_404(Formulario, id=formulario_id)
    usuario = request.user

    # Solo alumnos (role=student) o superuser
    if getattr(usuario, "role", None) != "student" and not usuario.is_superuser:
        return HttpResponseForbidden("Solo los alumnos pueden responder este formulario.")

    # Evitar que responda dos veces
    if Evaluacion.objects.filter(usuario=usuario, formulario=formulario).exists():
        messages.info(request, "Ya has respondido este formulario.")
        return redirect("cursos:detalle_formulario", pk=formulario.id)

    # Traer preguntas del formulario
    preguntas = (
        Pregunta.objects
        .filter(formulario=formulario)
        .prefetch_related("opciones")
        .order_by("orden")
    )

    if not preguntas:
        messages.info(request, "Este formulario aún no tiene preguntas configuradas.")
        return redirect("cursos:detalle_formulario", pk=formulario.id)

    if request.method == "POST":
        # 👈 OJO: aquí va 'preguntas', sin typo
        form = ResponderFormularioForm(request.POST, preguntas=preguntas)

        if form.is_valid():
            # Crear la evaluación (intento del alumno)
            evaluacion = Evaluacion.objects.create(
                usuario=usuario,
                formulario=formulario,
            )

            correctas = 0
            total_preguntas = len(preguntas)

            for pregunta in preguntas:
                field_name = f"pregunta_{pregunta.id}"

                es_correcta = False
                respuesta_texto = None
                opcion = None

                if pregunta.tipo == Pregunta.TIPO_ABIERTA:
                    # PREGUNTA ABIERTA
                    texto = (form.cleaned_data.get(field_name) or "").strip()
                    respuesta_texto = texto

                    # Si hay respuesta_esperada definida, comparamos
                    if pregunta.respuesta_esperada:
                        if es_similar(pregunta.respuesta_esperada, texto):
                            es_correcta = True

                    # Guardamos la respuesta de texto
                    RespuestaAlumno.objects.create(
                        evaluacion=evaluacion,
                        pregunta=pregunta,
                        respuesta_texto=texto,
                    )

                else:
                    # PREGUNTA SELECCIÓN MÚLTIPLE
                    opcion_id = form.cleaned_data.get(field_name)
                    try:
                        opcion = OpcionRespuesta.objects.get(
                            id=opcion_id,
                            pregunta=pregunta,
                        )
                    except (OpcionRespuesta.DoesNotExist, TypeError, ValueError):
                        opcion = None

                    RespuestaAlumno.objects.create(
                        evaluacion=evaluacion,
                        pregunta=pregunta,
                        opcion=opcion,
                    )

                    if opcion and opcion.es_correcta:
                        es_correcta = True

                if es_correcta:
                    correctas += 1

            # calcular puntaje (0-100%) considerando TODAS las preguntas
            puntaje = (correctas / total_preguntas) * 100 if total_preguntas > 0 else 0
            evaluacion.puntaje = puntaje

            # Regla de aprobación: 60% o más (se puede cambiar)
            evaluacion.aprobado = puntaje >= 60
            evaluacion.save()

            messages.success(
                request,
                f"Evaluación enviada. Tu puntaje fue {puntaje:.2f}%.",
            )
            return redirect("cursos:detalle_formulario", pk=formulario.id)
    else:
        # GET: mostrar el formulario vacío para responder
        form = ResponderFormularioForm(preguntas=preguntas)

    # Render tanto para GET como para POST inválido
    return render(
        request,
        "cursos/responder_formulario.html",
        {
            "formulario": formulario,
            "form": form,
            "preguntas": preguntas,
        },
    )


@login_required
def respuestas_formulario(request, formulario_id):
    """
    Vista para que DOCENTES / ADMIN vean las respuestas de los alumnos
    a un formulario.
    """
    formulario = get_object_or_404(Formulario, id=formulario_id)

    user = request.user
    if getattr(user, "role", None) not in ("teacher", "admin") and not user.is_superuser:
        return HttpResponseForbidden(
            "Solo docentes o administradores pueden ver las respuestas."
        )

    # Traemos las evaluaciones con sus respuestas
    evaluaciones = (
        Evaluacion.objects
        .filter(formulario=formulario)
        .select_related("usuario")
        .prefetch_related("respuestas__pregunta", "respuestas__opcion")
        .order_by("-fecha")
    )

    return render(
        request,
        "cursos/respuestas_formulario.html",
        {
            "formulario": formulario,
            "evaluaciones": evaluaciones,
        },
    )



class ActualizarProgresoModulo(APIView):

    def post(self, request, modulo_id):
        usuario = request.user
        porcentaje = request.data.get("progreso")

        if porcentaje is None:
            return Response({"error": "Debe enviar el porcentaje de progreso."}, status=400)

        progreso, creado = ProgresoModulo.objects.get_or_create(
            usuario=usuario,
            modulo_id=modulo_id
        )

        progreso.progreso = int(porcentaje)
        progreso.save()     # ← aquí se ejecuta el AUTO-COMPLETADO

        return Response({
            "modulo": progreso.modulo.titulo,
            "progreso": progreso.progreso,
            "estado": progreso.estado,
        })
@login_required
def crear_formulario(request,contenido_id):
    contenido = get_object_or_404(Contenido, pk=contenido_id)

    #solo docente/admin pueden crear Formulario
    if request.user.role not in ["teacher", "admin"]:
        return redirect("cursos:detalle", pk=contenido.modulo.curso.pk)
    if request.method == "POST":
        form = FormularioForm(request.POST)
        if form.is_valid():
            formulario = form.save(commit=False)
            formulario.contenido = contenido
            formulario.save()
            return redirect("cursos:editar_preguntas_formulario", formulario.pk)
        else:
            form = FormularioForm()
        return render(request, "cursos/formulario_form.html",{
            "form":form,
            "contenido": contenido,
        })
    
def es_similar(texto_ref, texto_alumno, umbral=0.7):
    """
    compara si la respuesta del alumno es 'parecida' a la respuesta esperada.
    Devuelve True si la similitud es mayor o igual al umbral (0.7 = 70%).
    """
    if not texto_ref or not texto_alumno:
        return False
    texto_ref = texto_ref.lower().strip()
    texto_alumno = texto_alumno.lower().strip()

    ratio = SequenceMatcher(None, texto_ref, texto_alumno).ratio()
    return ratio >= umbral