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


class TVView(TemplateView, TournamentDetail):
    template_name = 'tv.html'

    def get_context_data(self, **kwargs):
        context = {
            'tournament' : self.tournament,
            'divisions' : self.tournament.division_set.all(),
         }

        return context


class PrintsView(TemplateView, TournamentDetail):
    template_name = 'prints.html'

    def get_context_data(self, **kwargs):

        last_schedule = []
        for d in self.tournament.division_set.all():
            for g in d.group_set.all():
                # posledni schedule skupiny
                ls = g.LastSchedule

                last_schedule.append({
                        'schedule'      : ls,
                        'match'         : ls.match,
                        'pitch'         : ls.pitch,
                        'division'      : ls.match.division,
                        'group'         : ls.match.group,
                        'group_match_count'   : ls.match.group.match_set.count(),
                        })

        last_schedule.sort(key=lambda s: s['schedule'].time)

        context = {
            'tournament' : self.tournament,
            'last_schedule' : last_schedule,
            'user_role' : self.user_role,
        }

        return context
