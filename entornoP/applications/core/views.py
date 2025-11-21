from django.shortcuts import render
from django.db import models

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
