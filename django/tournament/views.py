from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from .models import Tournament

# Create your views here.

class TournamentListView(ListView):
    template_name = 'tournament-list.html'
    queryset = Tournament.objects.all()
    context_object_name = 'tournaments'

class TournamentDetailView(TemplateView):

    template_name = 'tournament_detail.html'

    def get_context_data(self, **kwargs):

        tournament = Tournament.objects.get(id=self.kwargs['id'])

        division_seed = {
            div : [
                seed.teamPlaceholder.team_name
                for seed in div.divisionseed_set.all()
            ]
            for div in tournament.division_set.all()
        }

        context = {
            'tournament' : tournament,
            'division_seed' : division_seed,
            #''

        }

        return context
