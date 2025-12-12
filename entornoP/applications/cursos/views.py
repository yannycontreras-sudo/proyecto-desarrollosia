from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import Avg
import csv
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from difflib import SequenceMatcher
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


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
    Simulacion,
    ProgresoSimulacion,
    
)

User= get_user_model()


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

        # Todos los módulos del curso ordenados
        modulos = (
            Modulo.objects
            .filter(curso=curso)
            .order_by("orden")
            .prefetch_related("contenidos")
        )

        # Si es alumno, solo ve módulos publicados
        if getattr(user, "role", None) in ["student", "alumno"] and not user.is_superuser:
            modulos = modulos.filter(publicado=True)

        context["modulos"] = modulos
        context["esta_inscrito"] = Inscripcion.objects.filter(
            usuario=user,
            curso=curso
        ).exists()

        # 👇 NUEVO: Calcular módulos desbloqueados para estudiantes
        if getattr(user, "role", None) in ["student", "alumno"]:
            modulos_desbloqueados = self.obtener_modulos_desbloqueados(
                user, modulos)
            context["modulos_desbloqueados"] = modulos_desbloqueados
        else:
            # Docentes/admin ven todos los módulos como desbloqueados
            context["modulos_desbloqueados"] = [m.id for m in modulos]

        return context

    def obtener_modulos_desbloqueados(self, usuario, modulos):
        """
        Devuelve lista de IDs de módulos que el estudiante puede acceder.
        El primer módulo siempre está desbloqueado.
        Los demás se desbloquean al completar el anterior.
        """
        modulos_list = list(modulos)
        if not modulos_list:
            return []

        desbloqueados = []

        for idx, modulo in enumerate(modulos_list):
            if idx == 0:
                # El primer módulo siempre está desbloqueado
                desbloqueados.append(modulo.id)
            else:
                # Verificar si completó el módulo anterior
                modulo_anterior = modulos_list[idx - 1]
                progreso_anterior = ProgresoModulo.objects.filter(
                    usuario=usuario,
                    modulo=modulo_anterior,
                    estado="completado"
                ).exists()

                if progreso_anterior:
                    desbloqueados.append(modulo.id)
                else:
                    # Si no completó el anterior, los siguientes tampoco están desbloqueados
                    break

        return desbloqueados


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

# ... arriba está CursoUpdateView ...


@login_required
def curso_confirmar_eliminar(request, pk):
    """
    Muestra una pantalla de confirmación ANTES de eliminar el curso.
    """
    curso = get_object_or_404(Curso, pk=pk)

    # Solo docentes, admins o superuser pueden eliminar
    user = request.user
    if getattr(user, "role", None) not in ("teacher", "admin") and not user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para eliminar cursos.")

    return render(request, "cursos/curso_confirmar_eliminar.html", {
        "curso": curso
    })


@login_required
def curso_eliminar(request, pk):
    """
    Elimina el curso SOLO si viene de un POST del formulario de confirmación.
    """
    curso = get_object_or_404(Curso, pk=pk)

    user = request.user
    if getattr(user, "role", None) not in ("teacher", "admin") and not user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para eliminar cursos.")

    if request.method == "POST":
        nombre = curso.nombre
        curso.delete()
        messages.success(request, f"El curso «{nombre}» fue eliminado correctamente.")
        return redirect("cursos:lista")

    # Si alguien entra por GET a esta URL, lo mando al detalle
    return redirect("cursos:detalle", pk=pk)


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
                respuesta_esperada = (form.cleaned_data.get(
                    "respuesta_esperada") or "").strip()

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
                        op_text = (form.cleaned_data.get(
                            f"opcion_{i}") or "").strip()
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

            messages.success(
                request, "Preguntas del formulario actualizadas correctamente.")
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

    # Acepta estudiantes creados como "student" o "alumno"
    if getattr(usuario, "role", None) not in ["student", "alumno"] and not usuario.is_superuser:
        return HttpResponseForbidden("Solo los alumnos pueden responder este formulario.")

    # Evitar que responda dos veces
    if Evaluacion.objects.filter(usuario=usuario, formulario=formulario).exists():
        messages.info(request, "Ya has respondido este formulario.")
        return redirect("cursos:resultado_formulario", formulario_id=formulario.id)

    # Traer preguntas del formulario
    preguntas = (
        Pregunta.objects
        .filter(formulario=formulario)
        .prefetch_related("opciones")
        .order_by("orden")
    )

    if not preguntas:
        messages.info(
            request, "Este formulario aún no tiene preguntas configuradas.")
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
            puntaje = (correctas / total_preguntas) * \
                100 if total_preguntas > 0 else 0
            evaluacion.puntaje = puntaje

                    # Regla de aprobación: 60% o más (se puede cambiar)
            evaluacion.aprobado = puntaje >= 60
            evaluacion.save()

            # FINALIZAR SIMULACIÓN SI PROVIENE DE UNA
            simulacion = getattr(formulario, "simulacion", None)
            if simulacion:
                progreso = ProgresoSimulacion.objects.filter(
                    usuario=usuario,
                    simulacion=simulacion,
                 estado="iniciada"
                ).first()

                if progreso:
                    progreso.estado = "completada"
                    progreso.fecha_fin = timezone.now()
                    progreso.save()


        # === NUEVO: actualizar ProgresoModulo para desbloquear el siguiente ===
        # El formulario pertenece a un contenido, y ese contenido a un módulo
            modulo = formulario.contenido.modulo

        # Obtenemos (o creamos) el progreso del alumno en este módulo
            progreso_modulo, creado = ProgresoModulo.objects.get_or_create(
                usuario=usuario,
                modulo=modulo,
                )
            if evaluacion.aprobado:
            # Si aprobó, dejamos el módulo como completado (100%)
             progreso_modulo.progreso = 100
            else:
            # Si quieres marcar algo cuando reprueba, puedes ajustar aquí.
            # Por ahora, si ya tenía un progreso mayor, no lo bajamos.
               if progreso_modulo.progreso is None or progreso_modulo.progreso < 50:
                    progreso_modulo.progreso = 50  # opcional, solo ejemplo
                    progreso_modulo.save()
        # ==============================================

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
# ======================================
# REPORTES DE DESEMPEÑO (DOCENTE / ADMIN)
# ======================================

@login_required
def reportes_desempeno(request):
    """
    Vista para que DOCENTES / ADMIN vean reportes de progreso y rendimiento.
    Incluye filtros y datos para gráficos.
    """
    user = request.user
    if getattr(user, "role", None) not in ("teacher", "admin") and not user.is_superuser:
        return HttpResponseForbidden("Solo docentes o administradores pueden ver reportes.")

    curso_id = request.GET.get("curso")
    docente_id = request.GET.get("docente")
    periodo = request.GET.get("periodo")

    # Base: todas las evaluaciones con relaciones necesarias
    evaluaciones = (
        Evaluacion.objects
        .select_related(
            "usuario",
            "formulario",
            "formulario__contenido__modulo__curso",
        )
        .all()
    )

    # ---- filtros ----
    if curso_id:
        evaluaciones = evaluaciones.filter(
            formulario__contenido__modulo__curso_id=curso_id
        )

    if docente_id:
        # Ojo: aquí asumo que Curso tiene un M2M "docentes"
        # si en tu modelo se llama distinto, cambia "docentes"
        evaluaciones = evaluaciones.filter(
            formulario__contenido__modulo__curso__docentes__id=docente_id
        )

    if periodo:
        # EJEMPLO: si tu "periodo" es el año (2024, 2025, etc.)
        # Ajusta esto según cómo lo guardes en tu modelo
        evaluaciones = evaluaciones.filter(fecha__year=periodo)

    # Agregar promedio de puntaje por curso (para el gráfico)
    datos_por_curso = (
        evaluaciones
        .values(
            "formulario__contenido__modulo__curso__id",
            "formulario__contenido__modulo__curso__nombre",
        )
        .annotate(promedio_puntaje=Avg("puntaje"))
        .order_by("formulario__contenido__modulo__curso__nombre")
    )

    etiquetas = [
        d["formulario__contenido__modulo__curso__nombre"]
        for d in datos_por_curso
    ]
    promedios = [
        float(d["promedio_puntaje"] or 0) for d in datos_por_curso
    ]

    cursos = Curso.objects.all()
    docentes = User.objects.filter(role="teacher")

    context = {
        "cursos": cursos,
        "docentes": docentes,
        "etiquetas": etiquetas,
        "promedios": promedios,
        "evaluaciones": evaluaciones,
    }
    return render(request, "cursos/reportes_desempeno.html", context)


@login_required
def exportar_reporte_csv(request):
    """
    Exporta el mismo reporte anterior a CSV.
    Usa los mismos filtros (curso, docente, periodo).
    """
    user = request.user
    if getattr(user, "role", None) not in ("teacher", "admin") and not user.is_superuser:
        return HttpResponseForbidden("Solo docentes o administradores pueden exportar reportes.")

    curso_id = request.GET.get("curso")
    docente_id = request.GET.get("docente")
    periodo = request.GET.get("periodo")

    evaluaciones = (
        Evaluacion.objects
        .select_related(
            "usuario",
            "formulario",
            "formulario__contenido__modulo__curso",
        )
        .all()
    )

    if curso_id:
        evaluaciones = evaluaciones.filter(
            formulario__contenido__modulo__curso_id=curso_id
        )

    if docente_id:
        evaluaciones = evaluaciones.filter(
            formulario__contenido__modulo__curso__docentes__id=docente_id
        )

    if periodo:
        evaluaciones = evaluaciones.filter(fecha__year=periodo)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=reporte_desempeno.csv"

    writer = csv.writer(response)
    writer.writerow(["Curso", "Alumno", "Puntaje", "Fecha"])

    for e in evaluaciones:
        curso = e.formulario.contenido.modulo.curso
        alumno = e.usuario.get_full_name() or e.usuario.username
        fecha_str = e.fecha.strftime("%Y-%m-%d") if hasattr(e, "fecha") and e.fecha else ""
        writer.writerow([curso.nombre, alumno, e.puntaje, fecha_str])

    return response


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
def crear_formulario(request, contenido_id):
    contenido = get_object_or_404(Contenido, pk=contenido_id)

    # Solo docente/admin pueden crear Formulario
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

    return render(
        request,
        "cursos/formulario_form.html",
        {
            "form": form,
            "contenido": contenido,
        }
    )


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


@login_required
def resultado_formulario(request, formulario_id):
    usuario = request.user
    formulario = get_object_or_404(Formulario, id=formulario_id)

    try:
        evaluacion = Evaluacion.objects.get(usuario=usuario, formulario=formulario)
    except Evaluacion.DoesNotExist:
        messages.error(request, "Aún no has respondido este formulario.")
        return redirect("cursos:detalle_formulario", pk=formulario.id)

    # Obtener respuestas
    respuestas = RespuestaAlumno.objects.filter(
        evaluacion=evaluacion
    ).select_related("pregunta", "opcion")

    # ==========================================================
    # LÓGICA PARA BUSCAR EL SIGUIENTE MÓDULO
    # ==========================================================
    modulo_actual = formulario.contenido.modulo
    curso = modulo_actual.curso

    modulos = list(curso.modulos.order_by("orden"))

    siguiente_modulo = None
    for index, mod in enumerate(modulos):
        if mod.id == modulo_actual.id and index + 1 < len(modulos):
            siguiente_modulo = modulos[index + 1]
            break

    # ==========================================================

    return render(request, "cursos/resultado_formulario.html", {
        "formulario": formulario,
        "evaluacion": evaluacion,
        "respuestas": respuestas,
        "siguiente_modulo": siguiente_modulo,  # 🔥 SE ENVÍA AL TEMPLATE
    })


@login_required
def mis_notas_view(request):
    """
    Vista para que el ESTUDIANTE vea su historial de calificaciones
    en formularios / simulaciones del curso.
    """
    usuario = request.user

    # Solo estudiantes (o superuser, por si quieres testear)
    if getattr(usuario, "role", None) not in ["student", "alumno"] and not usuario.is_superuser:
        messages.error(request, "Solo los estudiantes pueden ver su historial de calificaciones.")
        return redirect("core:home")

    # Traer todas las evaluaciones del alumno
    evaluaciones = (
        Evaluacion.objects
        .filter(usuario=usuario)
        .select_related(
            "formulario",
            "formulario__contenido",
            "formulario__contenido__modulo",
            "formulario__contenido__modulo__curso",
        )
        .order_by("-fecha")
    )

    context = {
        "evaluaciones": evaluaciones,
    }
    return render(request, "cursos/mis_notas.html", context)


@login_required
def iniciar_simulacion(request, simulacion_id):
    """
    Vista para que el ESTUDIANTE inicie una simulación.
    Ahora:
    - Valida permisos e inscripción
    - Registra progreso
    - Muestra los contenidos del módulo (videos / imágenes)
    - Desde ahí el alumno pasa a la evaluación (formulario)
    """
    simulacion = get_object_or_404(Simulacion, id=simulacion_id)
    usuario = request.user

    # Verificar que sea estudiante
    if getattr(usuario, "role", None) not in ["student", "alumno"] and not usuario.is_superuser:
        return HttpResponseForbidden("Solo los estudiantes pueden iniciar simulaciones.")

    # Verificar que esté inscrito en el curso
    modulo = simulacion.modulo
    curso = modulo.curso

    if not Inscripcion.objects.filter(usuario=usuario, curso=curso).exists():
        messages.error(request, "No estás inscrito en este curso.")
        return redirect("core:home")

    # Verificar que el módulo esté publicado
    if not modulo.publicado:
        messages.error(request, "Este módulo no está disponible aún.")
        return redirect("cursos:detalle", pk=curso.pk)

    # Verificar que la simulación tenga un formulario asociado
    if not hasattr(simulacion, "formulario") or not simulacion.formulario:
        messages.error(
            request,
            "Esta simulación no tiene un formulario configurado."
        )
        return redirect("cursos:detalle", pk=curso.pk)

    formulario = simulacion.formulario

    # Si YA respondió este formulario → no repetir, mandar directo a resultados
    evaluacion_existente = Evaluacion.objects.filter(
        usuario=usuario,
        formulario=formulario
    ).first()

    if evaluacion_existente:
        # Marcar progreso como completado si existe uno iniciado
        progreso, _ = ProgresoSimulacion.objects.get_or_create(
            usuario=usuario,
            simulacion=simulacion,
        )
        if progreso.estado != "completada":
            progreso.estado = "completada"
            if not progreso.fecha_fin:
                progreso.fecha_fin = timezone.now()
            progreso.save()

        messages.info(request, "Ya has realizado esta simulación.")
        return redirect("cursos:resultado_formulario", formulario_id=formulario.id)

    # Crear / actualizar progreso como INICIADA
    progreso, creado = ProgresoSimulacion.objects.get_or_create(
        usuario=usuario,
        simulacion=simulacion,
        defaults={"estado": "iniciada"},
    )

    if not creado:
        # Reinicio de intento (si lo permites): volvemos a estado iniciada
        progreso.estado = "iniciada"
        progreso.fecha_inicio = timezone.now()
        progreso.fecha_fin = None
        progreso.save()

    # 👉 NUEVO: en vez de ir directo a responder_formulario,
    # mostramos una página con los contenidos del módulo
    contenidos = modulo.contenidos.all().order_by("id")

    messages.success(request, f"Simulación '{simulacion.nombre}' iniciada.")

    return render(
        request,
        "cursos/simulacion_detalle.html",
        {
            "curso": curso,
            "modulo": modulo,
            "simulacion": simulacion,
            "formulario": formulario,
            "contenidos": contenidos,
        },
    )




@login_required
def asignar_simulacion_modulo(request, modulo_id):
    """
    Permite a un docente/admin elegir qué simulación se asocia a un módulo.
    """
    modulo = get_object_or_404(Modulo, pk=modulo_id)

    # Permisos: solo teacher, admin o superuser
    if not (
        getattr(request.user, "role", None) in ["teacher", "admin"]
        or request.user.is_superuser
    ):
        return HttpResponseForbidden("No tienes permisos para asignar simulaciones.")

    # Si tu modelo Simulacion tiene FK a Curso, puedes filtrar:
    # simulaciones = Simulacion.objects.filter(modulo__curso=modulo.curso).distinct()
    # Por ahora, usamos todas:
    simulaciones = Simulacion.objects.all()

    if request.method == "POST":
        simulacion_id = request.POST.get("simulacion_id")

        if simulacion_id:
            simulacion = get_object_or_404(Simulacion, pk=simulacion_id)
            modulo.simulacion = simulacion
            modulo.save()

            # Vuelta al detalle del curso
            return redirect("cursos:detalle", pk=modulo.curso.pk)

    # Si es GET o POST sin simulación elegida, mostramos el formulario
    context = {
        "modulo": modulo,
        "simulaciones": simulaciones,
    }
    return render(request, "cursos/asignar_simulacion.html", context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Modulo, Simulacion, Formulario  # ajusta import según tu organización


@login_required
def crear_simulacion(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)

    # Solo docentes / admins
    if request.user.role not in ["teacher", "admin"] and not request.user.is_superuser:
        return redirect("cursos:detalle", pk=modulo.curso.pk)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        formulario_id = request.POST.get("formulario")  # <--- OJO: name="formulario" en el template

        video = request.FILES.get("video")
        imagen = request.FILES.get("imagen")
        contenido_html = request.POST.get("contenido_html", "")

        # Si ya hay simulación para este módulo, la actualizamos
        if hasattr(modulo, "simulacion"):
            simulacion = modulo.simulacion
            simulacion.nombre = nombre
            simulacion.descripcion = descripcion
            if video:
                simulacion.video = video
            if imagen:
                simulacion.imagen = imagen
            simulacion.contenido_html = contenido_html
            simulacion.save()
        else:
            simulacion = Simulacion.objects.create(
                modulo=modulo,
                nombre=nombre,
                descripcion=descripcion,
                video=video,
                imagen=imagen,
                contenido_html=contenido_html,
            )

        # Asociar formulario si se eligió uno
        if formulario_id:
            try:
                formulario = Formulario.objects.get(pk=formulario_id)
                formulario.simulacion = simulacion
                formulario.save()
            except Formulario.DoesNotExist:
                pass

        return redirect("cursos:detalle", pk=modulo.curso.pk)

    # GET: aquí cargamos los formularios disponibles para ESTE módulo/curso
    # Si tus formularios están ligados a contenidos del módulo:
    formularios = Formulario.objects.filter(contenido__modulo=modulo).distinct()
    # Si quieres TODOS los formularios, usa:
    # formularios = Formulario.objects.all()

    simulacion_existente = getattr(modulo, "simulacion", None)

    return render(request, "cursos/crear_simulacion.html", {
        "modulo": modulo,
        "formularios": formularios,
        "simulacion": simulacion_existente,
    })
