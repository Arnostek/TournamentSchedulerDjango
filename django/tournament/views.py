from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from .models import Tournament, Division, Match
from django.db.models import Q
from django.http import HttpResponse

# Create your views here.

class TournamentListView(ListView):
    template_name = 'tournament-list.html'
    queryset = Tournament.objects.all()
    context_object_name = 'tournaments'

class TournamentDetailView(TemplateView):

    template_name = 'tournament_detail.html'

    def get_context_data(self, **kwargs):

        tournament = Tournament.objects.get(id=self.kwargs['tid'])

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

class DivisionSystemView(TemplateView):

    template_name = 'division_system.html'

    def get_context_data(self, **kwargs):

        division = Division.objects.get(id = self.kwargs['did'])

        groups = {

            group : [
                seed.teamPlaceholder.team_name
                for seed in group.groupseed_set.all()
            ]
            for group in division.group_set.all()
        }

        context = {
            'division' : division,
            'groups' : groups,
            'matches' : division.match_set.all().order_by('group__phase','phase_block','id')
        }

        return context

class ScheduleView(TemplateView):

    template_name = 'schedule.html'

    def get_context_data(self, **kwargs):

        tournament = Tournament.objects.get(id=self.kwargs['tid'])

        if 'did' in self.kwargs:
            schedules = tournament.schedule_set.filter(match__division__id = self.kwargs['did'])
        elif 'pid' in self.kwargs:
            schedules = tournament.schedule_set.filter(pitch__id = self.kwargs['pid'])
        elif 'team' in self.kwargs:
            schedules = tournament.schedule_set.filter(
                    Q(match__home__team__id = self.kwargs['team'])
                    | Q(match__away__team__id = self.kwargs['team'])
                    | Q(match__referee__team__id = self.kwargs['team'])
                )

        else:
            schedules = tournament.schedule_set.all()

        context = {
            'tournament' : tournament,
            'pitches' : tournament.pitch_set.all(),
            'schedules' : schedules,
        }

        return context

def SetScore(request, mid, who, score):
    #print (mid)
    m = Match.objects.get(id = mid)

    if who == 'home':
        m.home_score = score
        m.save()

    elif who == 'away':
        m.away_score = score
        m.save()

    return HttpResponse("OK")
