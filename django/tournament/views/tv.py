from django.views.generic import TemplateView
from .base import TournamentDetail


class TVView(TemplateView, TournamentDetail):
    template_name = 'tv.html'

    def get_context_data(self, **kwargs):
        context = {
            'tournament' : self.tournament,
            'divisions' : self.tournament.division_set.all(),
         }

        return context