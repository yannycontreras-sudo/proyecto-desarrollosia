from django.shortcuts import render
from django.db import models
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


# Create your views here.
from django.views.generic import (
    TemplateView,


)

class TimeStampedModel(models.Model):
    """Modelo abstracto con timestamps estándar."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class HomeView(TemplateView):
    template_name = "home.html"
