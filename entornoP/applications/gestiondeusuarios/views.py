from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages

from .forms import RegistroForm, LoginForm


def registro_view(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Opcional: si quieres que el alumno registrado vaya a sus cursos:
            role = getattr(user, "role", None)
            if role in ["student", "alumno"]:
                return redirect("cursos:mis_cursos")
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

            # si venía desde una página protegida, respeta ?next=
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)

            # si no hay 'next=', redirige según el rol
            role = getattr(user, "role", None)

            # Alumno → directo a sus cursos
            if role in ["student", "alumno"]:
                return redirect("core:home")

            # Docente → lista de cursos
            elif role in ["teacher", "docente"]:
                return redirect("core:home")

            # Admin → home
            elif role in ["admin", "administrador"]:
                return redirect("core:home")

            # Si por alguna razón no tiene rol conocido
            return redirect("core:home")
        else:
            messages.error(request, "Usuario o contraseña incorrecta.")
    else:
        form = LoginForm(request)

    return render(request, "gestiondeusuarios/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("gestiondeusuarios:login")
