from django.urls import path
from . import views

app_name = "tickets"

urlpatterns = [
    path('nuevo/', views.crear_ticket, name='crear_ticket'),
    path('mis-tickets/', views.lista_tickets, name='lista_tickets'),
]
