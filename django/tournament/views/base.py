from django.shortcuts import redirect
from django.http import Http404
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from ..models import Tournament, Division, Group, Match, Schedule, Pitch, Team, GroupTieRankingPoints
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date


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
