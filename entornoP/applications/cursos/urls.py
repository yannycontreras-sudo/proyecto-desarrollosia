from django.urls import path
from .views import (
    CursoListView,
    CursoDetailView,
    mis_cursos_view,
    inscribirse_curso_view,
    CursoCreateView,
)

app_name = "cursos"

urlpatterns = [
    path("", CursoListView.as_view(), name="lista"),
    path("mis-cursos/", mis_cursos_view, name="mis_cursos"),
    path("crear/", CursoCreateView.as_view(), name="crear"),
    path("<int:pk>/", CursoDetailView.as_view(), name="detalle"),
    path("<int:pk>/inscribirse/", inscribirse_curso_view, name="inscribirse"),
]