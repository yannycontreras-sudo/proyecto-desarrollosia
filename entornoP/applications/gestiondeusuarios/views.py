from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegistroForm, LoginForm, ProfileForm, AvatarSelectionForm
from .models import Avatar

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

@login_required
def editar_perfil(request):
    user = request.user

    # Validación básica de rol (opcional, la puedes ajustar)
    if getattr(user, "role", None) not in ["student", "alumno", "teacher", "admin"] and not user.is_superuser:
        messages.error(request, "No tienes permiso para editar este perfil.")
        return redirect("core:home")

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            # Ojo: sin espacio en el nombre de la url
            return redirect("gestiondeusuarios:editar_perfil")
    else:
        # GET → mostramos el formulario con los datos actuales del usuario
        form = ProfileForm(instance=user)

    # En ambos casos (GET o POST con errores) llegamos aquí
    return render(request, "gestiondeusuarios/editar_perfil.html", {"form": form})


@login_required
def elegir_avatar(request):
    user = request.user

    # Validar rol estudiante de forma robusta
    if user.role.lower().strip() not in ["alumno", "student"]:
        messages.error(request, "Solo los estudiantes pueden modificar su avatar.")
        return redirect("core:home")

    if request.method == "POST":
        form = AvatarSelectionForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Avatar actualizado correctamente.")
            return redirect("gestiondeusuarios:elegir_avatar")
    else:
        form = AvatarSelectionForm(instance=user)

    return render(request, "gestiondeusuarios/elegir_avatar.html", {"form": form})
