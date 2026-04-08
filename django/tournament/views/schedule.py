from django.views.generic import TemplateView
from django.http import Http404
from ..models import Tournament, Division, Group, Pitch, Team, Schedule
from django.db.models import Q
from django.utils.dateparse import parse_date
from .base import TournamentDetail


class ScheduleView(TemplateView, TournamentDetail):

    template_name = 'schedule.html'

    def get_context_data(self, **kwargs):

        filtered_for = None;
        tournament = self.tournament
        fdate = self.request.GET.get('filter_date')
        # mteam = self.request.GET.get('mark_team')
        # posledni zapas
        last_match_schedule = tournament.schedule_set.filter(match__isnull=False).order_by('time','pitch').last()
        # pocet hrist
        pitches = tournament.pitch_set.count()
        # schedule po posledni zapas
        schedules = tournament.schedule_set.all().order_by('time','pitch').filter(id__lte=last_match_schedule.id+pitches)
        highlight_team = None

        if 'did' in self.kwargs:
            if 'gid' in self.kwargs:
                schedules = schedules.filter(match__group__id = self.kwargs['gid'])
                filtered_for = '{} - Group {}'.format(Division.objects.get(id=self.kwargs['did']).name,Group.objects.get(id=self.kwargs['gid']).name)
            else:
                schedules = schedules.filter(match__division__id = self.kwargs['did'])
                filtered_for = '{}'.format(Division.objects.get(id=self.kwargs['did']).name)
        elif 'pid' in self.kwargs:
            schedules = schedules.filter(pitch__id = self.kwargs['pid'])
            filtered_for = '{}'.format(Pitch.objects.get(id=self.kwargs['pid']).name)
        elif 'team' in self.kwargs:
            schedules = schedules.filter(
                    Q(match__home__team__id = self.kwargs['team'])
                    | Q(match__away__team__id = self.kwargs['team'])
                    | Q(match__referee__team__id = self.kwargs['team'])
                )
            highlight_team = self.kwargs['team']
            filtered_for = '{}'.format(Team.objects.get(id=self.kwargs['team']).name)
        elif 'next' in self.kwargs:
              schedules = schedules.filter(
                    Q(match__home_score__isnull = True) 
                ).filter(
                    Q(match__isnull = False)
                )

        if fdate:
            schedules = schedules.filter(time__date=parse_date(fdate))
            filtered_for = (filtered_for or '') + ' - ' + fdate

        # all teams from all divisions
        teams = []
        for d in tournament.division_set.all():
            for s in d.divisionseed_set.all():
                if s.teamPlaceholder.team.id:
                    teams.append( {'id' : s.teamPlaceholder.team.id,
                                  'name' : s.teamPlaceholder.team.name + ' (' + s.division.slug + ')'} )

        context = {
            'tournament' : tournament,
            'pitches' : tournament.pitch_set.all(),
            'schedules' : schedules,
            'teams': teams,
            'highlight_team' : highlight_team,
            'filtered_for' : filtered_for,
            'user_role' : self.user_role,
            'last_match_schedule' : last_match_schedule
            # 'mark_team': mteam,
        }

        return context


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
