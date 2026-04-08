from django.views.generic import TemplateView
from django.http import Http404
from ..models import Division
from .base import TournamentDetail


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
