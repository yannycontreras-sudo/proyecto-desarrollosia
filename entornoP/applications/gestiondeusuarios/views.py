from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
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
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("core:home")
    else:
        form = LoginForm()
    return render(request, "gestiondeusuarios/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("gestiondeusuarios:login")