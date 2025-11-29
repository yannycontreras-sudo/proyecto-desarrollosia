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
            return redirect("core:home")
    else:
        form = RegistroForm()

    return render(request, "gestiondeusuarios/registro.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form =LoginForm(request, data=request.POST)
        if form.is_valid():
            user =form.get_user()
            login(request, user)


#si venia desde una pagina protegida, respeta ?next=
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
# si no hay 'next=, redirige segun el rol
            role= getattr(user, "role", None)

            if role == "student":
#aqui lo mandamos directo a sus cursos
                return redirect("cursos:mis_cursos")
            elif role == "teacher":
#docente a la lista de cursos 
                return redirect("cursos:lista")
            elif role == "admin":
#admin al home 
                return redirect("core:home")
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
