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
    ContenidoCreateView,
    ContenidoUpdateView,
    modulo_toggle_publicacion_view,
    FormularioDetailView,
    editar_preguntas_formulario,
    crear_pregunta,
    editar_pregunta,
    ActualizarProgresoModulo,
    responder_formulario,
    crear_formulario,
    respuestas_formulario,
    resultado_formulario,
)


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

    path(
        "<int:curso_pk>/modulos/crear/",
         ModuloCreateView.as_view(), 
         name="modulo_crear",
         ),

    path(
        "modulos/<int:pk>/editar/",
         ModuloUpdateView.as_view(), 
         name="modulo_editar",
         ),

    path(
        "modulos/<int:pk>/toggle-publicacion/",
         modulo_toggle_publicacion_view, 
         name="modulo_toggle_publicacion",
         ),

    path(
    "modulos/<int:modulo_id>/progreso/",
         ActualizarProgresoModulo.as_view(), 
         name="actualizar_progreso",
         ),


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

 

    # formularios (docente)

    path(
        "contenidos/<int:contenido_id>/formulario/crear/",
        crear_formulario,
        name="crear_formulario",
    ),

    path(
        "formularios/<int:pk>/",
        FormularioDetailView.as_view(),
        name="detalle_formulario",
    ),
    path(
        "formularios/<int:formulario_id>/preguntas/editar/",
        editar_preguntas_formulario,
        name="editar_preguntas_formulario",
    ),
   # mantener estos si sigues usando las vistas antiguas
    path(
        "formularios/<int:formulario_id>/preguntas/crear/",
        crear_pregunta,
        name="crear_pregunta",
    ),

    path(
        "pregunta/<int:pregunta_id>/editar/",
        editar_pregunta,
        name="editar_pregunta",
    ),

    #ver respuestas de un formulario (DOCENTE/ADMIN)
    path(
        "formularios/<int:formulario_id>/respuestas/",
        respuestas_formulario,
        name="respuestas_formulario",
    ),


    # responder formulario (alumno)
    path(
        "formularios/<int:formulario_id>/responder/",
        responder_formulario,
        name="responder_formulario",
    ),
    path(
        "formularios/<int:formulario_id>/resultado/",
        resultado_formulario, 
        name="resultado_formulario"
        ),

]