from django.shortcuts import render, redirect
from django.http import Http404
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from .models import Tournament, Division, Group, Match, Schedule, Pitch, Team, GroupTieRankingPoints
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
    def user_role(self):
        """role dle prihlaseneho uzivatele"""
        # zatim vsem prihlasenym vse
        return {
        'admin_menu'    : self.request.user.is_authenticated,
        # muze zadavat a mazat score
        'score_admin'   : self.request.user.is_authenticated,
        # muze uzavirat tabulky skupin
        'table_admin'   : self.request.user.is_authenticated,
        # muze menit zapasy
        'match_admin'   : self.request.user.is_authenticated,
        }

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
            'user_role' : self.user_role,
        }

        return context

class DivisionRankingView(TemplateView, TournamentDetail):

    template_name = 'division_ranking.html'

    def get_context_data(self, **kwargs):

        if 'did' in self.kwargs:

            try:
                division = Division.objects.get(id = self.kwargs['did'])
            except Division.DoesNotExist:
                raise Http404("This Division does not exist")

            rankings = [ {
                'division' : division,
                'ranking'  : division.divisionrank_set.all().order_by('rank')
            }
            ]

        else:

            rankings = []
            # dodat filtrovani na Turnaj
            for div in self.tournament.division_set.all():
                rankings.append({
                    'division' : div,
                    'ranking'  : div.divisionrank_set.all().order_by('rank')
                }

                )

        context = {
            'tournament' : self.tournament,
            'rankings' : rankings,
            'user_role' : self.user_role,
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
            # jen skupiny s vice nez jednim zapasem
            if group.match_set.count() > 1:
                tables[group] = {
                    'phase' : group.phase,
                    'results': group.ResultsDetail.to_html(classes="table crosstable table-bordered table-striped",justify="center"),
                }


        context = {
            'tournament' : self.tournament,
            'division' : division,
            'tables' : tables,
            'user_role' : self.user_role,
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
            'user_role' : self.user_role,
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


class ScheduleView(TemplateView, TournamentDetail):

    template_name = 'schedule.html'

    def get_context_data(self, **kwargs):

        filtered_for = None;
        tournament = self.tournament
        fdate = self.request.GET.get('filter_date')
        # mteam = self.request.GET.get('mark_team')
        schedules = tournament.schedule_set.all().order_by('time','pitch')
        highlight_team = None
        last_match_schedule = tournament.schedule_set.filter(match__isnull=False).order_by('time','pitch').last()


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

    elif who == 'away':
        m.away_score = score

    # final match needs winner
    if m.group.NeedsWinner and (m.home_score == m.away_score):
        if who == 'home':
            m.home_score = None
        elif who == 'away':
            m.away_score = None
        return HttpResponse("Error: Match needs winner!", status=400)

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

    return redirect(request.META.get('HTTP_REFERER'))




@login_required
def FinishGroup(request, gid):
    # nacteme skupinu a preklopime poradi do group ranks
    g = Group.objects.get(id = gid)

    if g.finished:
        return HttpResponse("Error: Group already finished!", status=400)

    g.FillRanks()

    return HttpResponse("OK")

@login_required
def ReopenGroup(request, gid):
    # nacteme skupinu a preklopime poradi do group ranks
    g = Group.objects.get(id = gid)

    if not g.finished:
        return HttpResponse("Error: Group is not finished!", status=400)

    g.finished = False
    g.save()

    return HttpResponse("OK")


@login_required
def AddTiePoints(request, gid, tphid):
    # nacteme skupinu
    g = Group.objects.get(id = gid)

    if g.finished:
        return HttpResponse("Error: Group is finished!", status=400)

    if not g.All_scores_filled:
        return HttpResponse("Error: All scores are not filled!", status=400)

    # vytvorime Tie Points
    g.CreateGroupTieRankingPoints()

    # nacteme prislusne group tie points
    gtp = GroupTieRankingPoints.objects.filter(group = g).get(tph__id = tphid)
    gtp.tiepoints += 1
    gtp.save()

    return HttpResponse("OK")

class ConflictsView(TemplateView):
    template_name = 'conflicts.html'

    def get_context_data(self, **kwargs):
        # nacteme Tournament
        tm = Tournament.objects.get(slug = self.kwargs['slug'])
        # conflicts
        conflicts = []
        # nacteni schedule do dataframe
        df = pd.DataFrame([{ 'time' : sch.time, 'pitch' : sch.pitch.name, 'match': sch.match }for sch in tm.schedule_set.all()])
        df = df.pivot(columns='pitch',index='time',values='match')
        # projdeme radky
        for i in range(len(df)-1):
            # projdeme hriste
            for p1 in range(len(df.columns)):
                m1 = df.iloc[i,p1]
                # chybejici rozhodci
                if m1 and not m1.referee:
                    conflicts.append({
                        "problem":"Missing referee",
                        "division":m1.division,
                        "group":m1.group,
                        "match":m1,
                        "schedule":m1.schedule_set.last(),
                        })
                # druhy zapas kontrolujeme na vsech hristich
                for p2 in range(len(df.columns)):
                    # stejny a nasledujici cas
                    for m2 in [df.iloc[i,p2],df.iloc[i+1,p2]]:
                        if m1 and m2 and m1 != m2:
                            for typ1,tph1 in [("play",m1.home),("play",m1.away),("ref",m1.referee)]:
                                for typ2,tph2 in [("play",m2.home),("play",m2.away),("ref",m2.referee)]:
                                    if tph1 == tph2 and tph1 != None:
                                        conflicts.append({
                                            "problem":"Team conflict - " + typ1 + " " + typ2,
                                            "division":m1.division,
                                            "group":m1.group,
                                            "match":m1,
                                            "schedule":m1.schedule_set.last(),
                                            "team":tph1,
                                            "match2":m2,
                                            })
        # data pro sablonu
        return {'conflicts':conflicts}

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
