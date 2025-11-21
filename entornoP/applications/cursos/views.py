from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Curso, Inscripcion, Modulo
from .forms import CursoForm


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

        # módulos y contenidos del curso
        modulos = (
            Modulo.objects
            .filter(curso=curso)
            .order_by("orden")
            .prefetch_related("contenidos")
        )
        context["modulos"] = modulos

        # saber si el usuario está inscrito
        user = self.request.user
        context["esta_inscrito"] = Inscripcion.objects.filter(
            usuario=user,
            curso=curso,
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
            messages.success(request, f"Te has inscrito en el curso: {curso.nombre}")
        else:
            messages.info(request, f"Ya estabas inscrito en el curso: {curso.nombre}")

        return redirect("cursos:detalle", pk=curso.pk)

    return redirect("cursos:detalle", pk=curso.pk)


class CursoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Curso
    form_class = CursoForm
    template_name = "cursos/curso_form.html"
    success_url = reverse_lazy("cursos:lista")

    def test_func(self):
        """Solo permiten crear cursos los docentes o admin."""
        user = self.request.user
        # Ajusta según tu modelo de usuario
        # Si tienes role = "teacher"/"admin":
        return getattr(user, "role", None) in ("teacher", "admin")

        # O si tienes métodos:
        # return user.is_teacher() or user.is_admin_role()

    def form_valid(self, form):
        # Guardamos el curso
        response = super().form_valid(form)

        # Agregar automáticamente al docente creador como docente del curso
        curso = self.object
        user = self.request.user
        curso.docentes.add(user)

        return response
