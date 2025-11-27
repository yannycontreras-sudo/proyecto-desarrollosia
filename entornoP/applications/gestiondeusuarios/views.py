from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages   

from .forms import RegistroForm, LoginForm
from cursos.models import Curso, Modulo, ProgresoModulo



def registro_view(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:home")
    else:
        form = RegistroForm()
    return render(request, "gestiondeusuarios/registro.html", {"form": form})



def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # si venías de una página protegida usa ?next=..., si no al home
            next_url = request.GET.get("next") or "core:home"
            return redirect(next_url)
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm(request)  # importante pasar request también aquí

    return render(request, "gestiondeusuarios/login.html", {"form": form})



def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("gestiondeusuarios:login")



@login_required
def ver_progreso(request):
    user = request.user

    cursos = Curso.objects.all()
    progreso_data = []

    for curso in cursos:
        modulos = Modulo.objects.filter(curso=curso)
        total_modulos = modulos.count()

        completados = ProgresoModulo.objects.filter(
            user=user, modulo__in=modulos, completado=True
        ).count()

        porcentaje = 0
        if total_modulos > 0:
            porcentaje = int((completados / total_modulos) * 100)

        progreso_data.append({
            "curso": curso,
            "total_modulos": total_modulos,
            "completados": completados,
            "porcentaje": porcentaje
        })

    return render(request, "gestiondeusuarios/progreso.html", {
        "progreso_data": progreso_data
    })
