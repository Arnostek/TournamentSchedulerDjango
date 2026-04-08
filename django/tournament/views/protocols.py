from django.views.generic import TemplateView
from django.http import Http404
from ..models import Tournament, Division, Group, Pitch, Team, Schedule
from django.db.models import Q
from django.utils.dateparse import parse_date
from .base import TournamentDetail


class ProtocolsView(TemplateView, TournamentDetail):

    template_name = 'protocols.html'

    def get_context_data(self, **kwargs):

        matches = []
        schedules = []

        if 'pid' in self.kwargs:
            try:
                schedules = Schedule.objects.filter(pitch = self.kwargs['pid'])
            except Pitch.DoesNotExist:
                raise Http404("This pitch does not exist")

        if 'gid' in self.kwargs:
            try:
                schedules = Schedule.objects.filter(match__group = self.kwargs['gid'])
            except Group.DoesNotExist:
                raise Http404("This group does not exist")

        if 'did' in self.kwargs:
            try:
                schedules = Schedule.objects.filter(match__division = self.kwargs['did'],match__group__phase = self.kwargs['phase'])
            except Group.DoesNotExist:
                raise Http404("This group does not exist")

        # pripravime data pro sablonu
        for s in schedules:
            if s.match and not s.match.score_filled:
                matches.append({
                'number' : s.game_number,
                'division' : s.match.division.name,
                'group' : s.match.group.name,
                'team1' : s.match.home.team_name,
                'team2' : s.match.away.team_name,
                'ref' : s.match.referee.team_name if s.match.referee else '',
                'pitch' : s.pitch.name,
                'time' : s.time,
                'phase' : s.match.group.phase,
                'tournament' : s.match.division.tournament.name,
                'final_match' : s.match.group.NeedsWinner,
                })

        return {'matches' : matches}