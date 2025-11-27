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
    modulo_toggle_publicacion_view,
    ContenidoCreateView,
    ContenidoUpdateView,
    subir_recurso,
    ver_modulo,
)
from . import views

app_name = "cursos"

urlpatterns = [
    # cursos
    path("", CursoListView.as_view(), name="lista"),
    path("mis-cursos/", mis_cursos_view, name="mis_cursos"),
    path("crear/", CursoCreateView.as_view(), name="crear"),
    path("<int:pk>/", CursoDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", CursoUpdateView.as_view(), name="editar"),
    path("<int:pk>/inscribirse/", inscribirse_curso_view, name="inscribirse"),

    # módulos
    path("<int:curso_pk>/modulos/crear/", ModuloCreateView.as_view(), name="modulo_crear"),
    path("modulos/<int:pk>/editar/", ModuloUpdateView.as_view(), name="modulo_editar"),
    path("modulos/<int:pk>/toggle-publicacion/", modulo_toggle_publicacion_view, name="modulo_toggle_publicacion"),

    # contenidos
    path(
        "modulos/<int:modulo_pk>/contenidos/crear/",
        ContenidoCreateView.as_view(),
        name="contenido_crear",
    ),
    path(
        "contenidos/<int:pk>/editar/",
        ContenidoUpdateView.as_view(),
        name="contenido_editar",
    ),
    # Subida de Archivos
    path("subir-recurso/", subir_recurso, name="subir_recurso"),
    path("modulo/<int:modulo_id>/", ver_modulo, name="ver_modulo"),
]
