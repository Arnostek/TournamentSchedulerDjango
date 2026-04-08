from django.views.generic import TemplateView
from ..models import Tournament
from .base import TournamentDetail


class TournamentDetailView(TemplateView, TournamentDetail):

    template_name = 'tournament_detail.html'

    def get_context_data(self, **kwargs):

        division_seed = {
            div : [
            {
            'name' :    seed.teamPlaceholder.team_name,
            'id' :    seed.teamPlaceholder.team_id
                }
                for seed in div.divisionseed_set.all()
            ]
            for div in self.tournament.division_set.all()
        }

        context = {
            'tournament' : self.tournament,
            'division_seed' : division_seed,
            'user_role' : self.user_role,
        }

        return context
