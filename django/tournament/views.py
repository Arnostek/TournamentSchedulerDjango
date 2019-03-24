from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Tournament

# Create your views here.

class TournamentListView(ListView):
    template_name = 'tournament-list.html'
    queryset = Tournament.objects.all()
    context_object_name = 'tournaments'
