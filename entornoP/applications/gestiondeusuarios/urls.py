from django.urls import path
from . import views

app_name = "gestiondeusuarios"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("registro/", views.registro_view, name="registro"),
    path("perfil/", views.editar_perfil, name="editar_perfil"),
    path("avatar/", views.elegir_avatar, name="elegir_avatar"),
]
