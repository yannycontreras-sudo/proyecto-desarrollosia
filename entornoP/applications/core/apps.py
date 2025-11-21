from django.urls import path
from .views import HomeView  # importa SOLO la vista, nada de importar core.urls

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]