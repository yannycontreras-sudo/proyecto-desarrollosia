from django.urls import path
from .views import (
    CursoListView,
    CursoDetailView,
    mis_cursos_view,
    inscribirse_curso_view,
    CursoCreateView,
    CursoUpdateView,
    ModuloCreateView,
    ModuloUpdateView,
)

app_name = "cursos"

urlpatterns = [
    path("", CursoListView.as_view(), name="lista"),
    path("mis-cursos/", mis_cursos_view, name="mis_cursos"),
    path("crear/", CursoCreateView.as_view(), name="crear"),
    path("<int:pk>/", CursoDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", CursoUpdateView.as_view(), name="editar"),
    path("<int:pk>/inscribirse/", inscribirse_curso_view, name="inscribirse"),

    # módulos
    path("<int:curso_pk>/modulos/crear/", ModuloCreateView.as_view(), name="modulo_crear"),
    path("modulos/<int:pk>/editar/", ModuloUpdateView.as_view(), name="modulo_editar"),
]