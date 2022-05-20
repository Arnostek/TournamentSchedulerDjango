from django.shortcuts import render, redirect
from django.http import Http404
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from .models import Tournament, Division, Group, Match, Schedule
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils.dateparse import parse_date
import pandas as pd

# Create your views here.


class TournamentListView(ListView):
    template_name = 'tournament-list.html'
    queryset = Tournament.objects.all()
    context_object_name = 'tournaments'

class TournamentDetail:

    @property
    def tournament(self):
        try:
            tournament = Tournament.objects.get(slug=self.kwargs['slug'])
        except Tournament.DoesNotExist:
            raise Http404("This Tournament does not exist")
        return tournament

class TournamentDetailView(TemplateView, TournamentDetail):

    template_name = 'tournament_detail.html'

    def get_context_data(self, **kwargs):

        division_seed = {
            div : [
                seed.teamPlaceholder.team_name
                for seed in div.divisionseed_set.all()
            ]
            for div in self.tournament.division_set.all()
        }

        context = {
            'tournament' : self.tournament,
            'division_seed' : division_seed,
        }

        return context

class DivisionSystemView(TemplateView, TournamentDetail):

    template_name = 'division_system.html'

    def get_context_data(self, **kwargs):
        try:
            division = Division.objects.get(id = self.kwargs['did'])
        except Division.DoesNotExist:
            raise Http404("This Division does not exist")
        groups = {

            group : [
                seed.teamPlaceholder.team_name
                for seed in group.groupseed_set.all()
            ]
            for group in division.group_set.all()
        }

        context = {
            'tournament' : self.tournament,
            'division' : division,
            'groups' : groups,
            'matches' : division.match_set.all().order_by('group__phase','phase_block','id'),
        }

        return context

class DivisionCrossTablesView(TemplateView, TournamentDetail):

    template_name = 'division_crosstables.html'

    def get_context_data(self, **kwargs):

        tables = {}

        try:
            division = Division.objects.get(id = self.kwargs['did'])
        except Division.DoesNotExist:
            raise Http404("This Division does not exist")

        for group in division.group_set.all():
            tables[group] = group.ResultsDetail.to_html(classes="table crosstable",justify="center")

        context = {
            'tournament' : self.tournament,
            'division' : division,
            'tables' : tables,
            'kpadmin' : self.request.user.is_authenticated,
        }

        return context

class DivisionTablesView(TemplateView, TournamentDetail):

    template_name = 'division_tables.html'

    def get_context_data(self, **kwargs):

        tables = {}

        try:
            division = Division.objects.get(id = self.kwargs['did'])
        except Division.DoesNotExist:
            raise Http404("This Division does not exist")

        for group in division.group_set.all():
            tables[group] = group.Results

        context = {
            'tournament' : self.tournament,
            'division' : division,
            'tables' : tables,
            'kpadmin' : self.request.user.is_authenticated,
        }

        return context


class ScheduleView(TemplateView, TournamentDetail):

    template_name = 'schedule.html'

    def get_context_data(self, **kwargs):

        tournament = self.tournament
        fdate = self.request.GET.get('filter_date')
        mteam = self.request.GET.get('mark_team')
        schedules = tournament.schedule_set.all().order_by('time','pitch')

        if 'did' in self.kwargs:
            if 'gid' in self.kwargs:
                schedules = schedules.filter(match__group__id = self.kwargs['gid'])
            else:
                schedules = schedules.filter(match__division__id = self.kwargs['did'])
        elif 'pid' in self.kwargs:
            schedules = schedules.filter(pitch__id = self.kwargs['pid'])
        elif 'team' in self.kwargs:
            schedules = schedules.filter(
                    Q(match__home__team__id = self.kwargs['team'])
                    | Q(match__away__team__id = self.kwargs['team'])
                    | Q(match__referee__team__id = self.kwargs['team'])
                )

        if fdate:
            schedules = schedules.filter(time__date=parse_date(fdate))

        # It´s so ugly please don´t hit me
        teams = []
        for s in tournament.schedule_set.all():
            if s.match:
                if s.match.home and s.match.home.team:
                    teams.append(s.match.home.team.name)
                if s.match.away and s.match.away.team:
                    teams.append(s.match.away.team.name)
                if s.match.referee and s.match.referee.team:
                    teams.append(s.match.referee.team.name)
        teams = sorted(set(teams))

        context = {
            'tournament' : tournament,
            'pitches' : tournament.pitch_set.all(),
            'schedules' : schedules,
            'kpadmin' : self.request.user.is_authenticated,
            'teams': teams,
            'mark_team': mteam,
        }

        return context

@login_required
def SetScore(request, mid, who, score):
    #print (mid)
    m = Match.objects.get(id = mid)

    if m.locked:
        return HttpResponse("Error: Match locked!", status=400)

    if score > 50:
        return HttpResponse("Error: Score > 50!", status=400)

    if who == 'home':
        m.home_score = score
        m.save()

    elif who == 'away':
        m.away_score = score
        m.save()

    return HttpResponse("OK")

@login_required
def DelScore(request, mid):
    """ Smazani score pro zapas"""
    m = Match.objects.get(id = mid)

    if m.locked:
        return HttpResponse("Error: Match locked!", status=400)

    m.home_score = None
    m.away_score = None
    m.save()

    return HttpResponse("OK")

@login_required
def SwitchMatch(request,  sid1, sid2):
    s1 = Schedule.objects.get(id = sid1)
    s2 = Schedule.objects.get(id = sid2)
    m1 = s1.match
    m2 = s2.match
    s1.match = m2
    s2.match = m1
    s1.save()
    s2.save()
    t = s1.tournament
    return redirect('/live/' + t.slug + '/schedule-full')



@login_required
def FinishGroup(request, gid):
    # nacteme skupinu a preklopime poradi do group ranks
    g = Group.objects.get(id = gid)

    if g.finished:
        return HttpResponse("Error: Group already finished!", status=400)

    g.FillRanks()

    return HttpResponse("OK")

def FindConflicts(request, tid):
    tm = Tournament.objects.get(id = tid)
    response = ""
    df = pd.DataFrame([{ 'time' : sch.time, 'pitch' : sch.pitch.name, 'match': sch.match }for sch in tm.schedule_set.all()])
    df = df.pivot(columns='pitch',index='time',values='match')
    for i in range(len(df)-1):
        for p1 in range(len(df.columns)):
            for p2 in range(len(df.columns)):
                m1 = df.iloc[i,p1]
                for m2 in [df.iloc[i,p2],df.iloc[i+1,p2]]:
                    if m1 and m2 and m1 != m2:
                        for tph1 in [m1.home,m1.away,m1.referee]:
                            for tph2 in [m2.home,m2.away,m2.referee]:
                                if tph1 == tph2 and tph1 != None:
                                    team_name = tph1
                                    if tph1 and tph1.team:
                                        team_name = tph1.team.name
                                    response += ("Problem match num #{} team {} in match # {}<br>".format(Schedule.objects.get(match=m1).game_number,team_name, Schedule.objects.get(match=m2).game_number))
    if response == "":
        response += "No conflicts found - yyiihhaaa"
    response += "<a href='/"+ tm.slug + "/schedule-full'>Back to the schedule</a>"
    return HttpResponse(response)
