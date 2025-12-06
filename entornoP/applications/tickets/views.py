from django.shortcuts import render
from .models import Ticket

from django.shortcuts import render, redirect
from .forms import TicketForm
from django.contrib.auth.decorators import login_required


@login_required
def crear_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.usuario = request.user  # asignar usuario automáticamente
            ticket.save()
            return redirect('tickets:lista_tickets')

    else:
        form = TicketForm()

    return render(request, 'tickets/crear_ticket.html', {'form': form})


@login_required
def lista_tickets(request):
    tickets = Ticket.objects.filter(usuario=request.user)
    return render(request, 'tickets/lista_tickets.html', {'tickets': tickets})
