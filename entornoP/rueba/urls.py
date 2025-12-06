# rueba/urls.py
"""
URL configuration for rueba project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),

    # HOME (usa applications.core.urls → HomeView → home.html)
    path('', include('applications.core.urls')),

    # Usuarios (login, registro, logout, etc.)
    path('accounts/', include('applications.gestiondeusuarios.urls')),

    # Cursos
    path("cursos/", include("applications.cursos.urls")),

    # tickets
    path('tickets/', include('applications.tickets.urls')),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
