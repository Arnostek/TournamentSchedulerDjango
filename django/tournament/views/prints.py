from django.views.generic import TemplateView
from .base import TournamentDetail


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