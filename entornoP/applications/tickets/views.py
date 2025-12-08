from django.shortcuts import render
from .models import Ticket

from django.shortcuts import render, redirect
from .forms import TicketForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings


@login_required
def crear_ticket(request):

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.usuario = request.user
            ticket.save()

            # Envío de correo
            send_mail(
                subject="Confirmación de Ticket de Soporte",
                message=(
                    f"Hola {request.user.username},\n\n"
                    f"Tu ticket ha sido recibido con éxito.\n\n"
                    f"ID Ticket: {ticket.id}\n"
                    f"Título: {ticket.titulo}\n"
                    f"Estado inicial: {ticket.estado}\n\n"
                    f"Gracias por contactarnos."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=True,
            )

            return redirect("tickets:lista_tickets")

    else:
        form = TicketForm()   # <- ESTE RETURN ES EL QUE FALTABA

    return render(request, "tickets/crear_ticket.html", {"form": form})



@login_required
def lista_tickets(request):
    tickets = Ticket.objects.filter(usuario=request.user)
    return render(request, 'tickets/lista_tickets.html', {'tickets': tickets})
