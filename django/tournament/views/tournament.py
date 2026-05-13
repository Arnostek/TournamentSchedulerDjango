from django.views.generic import TemplateView
from ..models import Tournament, Division, Group, Match


class TournamentProgressView(TemplateView):
    template_name = 'tournament_progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        tournament = Tournament.objects.get(slug=slug)

        # All matches in tournament
        all_matches = Match.objects.filter(division__tournament=tournament)
        played_matches = all_matches.filter(home_score__isnull=False, away_score__isnull=False)

        # Progress for whole tournament
        context['tournament_progress'] = {
            'played': played_matches.count(),
            'total': all_matches.count(),
        }

        # Progress per division
        divisions = Division.objects.filter(tournament=tournament)
        division_progress = []
        for division in divisions:
            div_matches = all_matches.filter(division=division)
            div_played = div_matches.filter(home_score__isnull=False, away_score__isnull=False)
            div_info = {
                'division': division,
                'played': div_played.count(),
                'total': div_matches.count(),
                'phases': [],
            }
            # Progress per phase in division
            phases = div_matches.values_list('group__phase', flat=True).distinct().order_by('group__phase')
            for phase in phases:
                phase_matches = div_matches.filter(group__phase=phase)
                phase_played = phase_matches.filter(home_score__isnull=False, away_score__isnull=False)
                phase_info = {
                    'phase': phase,
                    'played': phase_played.count(),
                    'total': phase_matches.count(),
                    'groups': [],
                }
                # Progress per group in phase
                groups = Group.objects.filter(division=division, phase=phase)
                for group in groups:
                    group_matches = phase_matches.filter(group=group)
                    group_played = group_matches.filter(home_score__isnull=False, away_score__isnull=False)
                    group_info = {
                        'group': group,
                        'played': group_played.count(),
                        'total': group_matches.count(),
                    }
                    phase_info['groups'].append(group_info)
                div_info['phases'].append(phase_info)
            division_progress.append(div_info)
        context['division_progress'] = division_progress
        context['tournament'] = tournament
        context['page_title'] = f"Progress: {tournament.name}"
        return context
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
            'page_title' : self.tournament.name
        }

        return context
