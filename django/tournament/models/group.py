from django.db import models
from ..polygon_generator import polygon_generator
from .team_placeholder import TeamPlaceholder
from .group_tie_ranking_points import GroupTieRankingPoints
from .match import Match


class Group(models.Model):
    name = models.CharField(max_length=200)
    division = models.ForeignKey('Division', on_delete=models.CASCADE)
    phase = models.PositiveSmallIntegerField()
    finished = models.BooleanField(default=False)
    referee_group = models.ForeignKey("self", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)

    @property
    def teams(self):
        return self.groupseed_set.all().count()

    def CreateRanks(self):
        # create SeedDivision
        for rank in range(self.teams):
            rank = rank + 1
            # pripravim si TeamPlaceholder
            tph = TeamPlaceholder()
            if self.teams == 2:
                wl = ['Winner', 'Loser']
                tph.name = "{} {}".format(wl[rank - 1], self.name)
            else:
                tph.name = "{}. gr {}".format(rank, self.name)
            tph.save()
            # zalozim DivisionSeed
            seed = self.grouprank_set.create(rank=rank, teamPlaceholder=tph)

    def CreateMatches(self):
        """ vytvoreni vsech zapasu ve skupine """
        # pokud jeste neexistuje zadny zapas
        if self.match_set.count() == 0:
            for zapas_tup in polygon_generator(self.teams):
                self.CreateMatch(zapas_tup)

    def CreateMatch(self, zapas_tup):
        """ Vytvoreni jednoho zapasu podle poradi seedu """
        self.match_set.create(
            division=self.division,
            group=self,
            phase_block=zapas_tup[2],
            home=self.groupseed_set.get(rank=zapas_tup[0]).teamPlaceholder,
            away=self.groupseed_set.get(rank=zapas_tup[1]).teamPlaceholder,
        )

    def CreateGroupTieRankingPoints(self):
        """ Vytvoreni zaznamu ExtrRankingPoints pro skupinu"""
        if self.grouptierankingpoints_set.count() == 0:
            for gs in self.groupseed_set.all():
                erp = GroupTieRankingPoints()
                erp.tph = gs.teamPlaceholder
                erp.group = self
                erp.tiepoints = 0
                erp.save()

    @property
    def Results(self):
        """ Vypocte body tymu ve skupine """
        self.GroupResults = {}

        # projdeme zapasy
        for match in self.match_set.all():
            self.AddTeamResult(match.home, match.home_points, match.home_score, match.away_score)
            self.AddTeamResult(match.away, match.away_points, match.away_score, match.home_score)

        # pokud jsou, pricteme body z predchozi skupiny
        for gpt in self.points_transfer_dst.all():
            # projdeme stare vysledky
            for old_tph, old_result in gpt.src.Results.items():
                # najdeme novy groupseed podle tymu
                new_gs_set = self.groupseed_set.filter(teamPlaceholder__team=old_tph.team)
                # pokud tym najdeme, pripocteme vysledky
                if len(new_gs_set) > 0:
                    self.AddTeamResult(
                        new_gs_set[0].teamPlaceholder,
                        old_result["points"],
                        old_result["scored"],
                        old_result["obtained"])
                    # doplnime pocet zapasu
                    for i in range(old_result["games"] - 1):
                        self.AddTeamResult(new_gs_set[0].teamPlaceholder, 0, 0, 0)

        # pokud existuji, pricteme body z GroupTieRankingPoints
        for erp in self.grouptierankingpoints_set.all():
            self.AddTeamResult(erp.tph, None, None, None, erp.tiepoints)

        # setridene dle poradi
        tmp = sorted(
            self.GroupResults.items(),
            key=lambda item: (
                int(item[1]['points']),
                int(item[1]['diff']),
                int(item[1]['scored']),
                int(item[1]['tiepoints']),
            ),
            reverse=True
        )
        # vracime v puvodni strukture
        return {tup[0]: tup[1] for tup in tmp}

    @property
    def ResultsDetail(self):
        """ Data pro cross tabulku zapasu"""
        import pandas as pd

        # seznam tph z groupy bereme z results - setridene dle poradi
        teams = [tph for tph in self.Results.keys()]
        # dataframe tabulky
        df = pd.DataFrame(index=teams, columns=teams)

        # naplneni zapasu
        for match in self.match_set.all():
            df.loc[match.home, match.away] = match
            df.loc[match.away, match.home] = match

        # df pro vysledky
        results = pd.DataFrame(index=df.index, columns=['Games', 'Points', 'Diff', 'Scored', 'Obtained', 'TiePoints', 'Rank'])

        # vysledky zapasu
        matches = pd.DataFrame(index=df.index, columns=df.columns)

        # napocteni bodu a vysledku
        for tph in df.index:

            # vysledky prebirame ze stare metody -
            results.loc[tph, 'Games'] = self.Results[tph]['games']
            results.loc[tph, 'Points'] = self.Results[tph]['points']
            results.loc[tph, 'Scored'] = self.Results[tph]['scored']
            results.loc[tph, 'Obtained'] = self.Results[tph]['obtained']
            results.loc[tph, 'TiePoints'] = self.Results[tph]['tiepoints']

            for tph_col in df.columns:

                m = df.loc[tph, tph_col]
                if isinstance(m, Match):
                    if m.score_filled:
                        matches.loc[tph, tph_col] = '{} : {}'.format(m.tph_scored(tph), m.tph_obtained(tph))
                    else:
                        matches.loc[tph, tph_col] = ' : '
                else:
                    matches.loc[tph, tph_col] = 'X'

        results['Diff'] = results['Scored'] - results['Obtained']
        # rank - setridime index a naplnime Rank
        rank_cols = ['Points', 'Diff', 'Scored', 'TiePoints']
        # results.loc[results.sort_values(by=rank_cols,ascending=False).index,'Rank'] = range(1,len(results)+1)
        results['Rank'] = results.sort_values(by=rank_cols, ascending=False).groupby(rank_cols, sort=False).ngroup() + 1
        # vse prevedeme na int
        results = results.astype(int)

        # join df
        matches = matches.join(results)

        # upravime indexy a columns
        matches.index = matches.index.map(lambda t: t.team_name)
        matches.columns = matches.columns.map(lambda t: t.team_name if isinstance(t, TeamPlaceholder) else t)

        # vracime dataframe setrideny dle poradi
        return matches.drop('TiePoints', axis=1)

    @property
    def Rank_conflict(self):
        """ Vysledky skupiny maji konflikt - potreba stanovit poradi jinak """
        # max poradi je mensi nez pocet tymu
        return self.ResultsDetail['Rank'].max() < self.teams

    @property
    def All_scores_filled(self):
        """ Jsou uz zadana score ze vsech zapasu skupiny? """

        for match in self.match_set.all():
            if not match.score_filled:
                return False

        return True

    def AddTeamResult(self, teamPlaceholder, points, scored, obtained, tiepoints=0):
        """ Pripocteni bodu pro jeden tym"""

        if teamPlaceholder not in self.GroupResults:
            self.GroupResults[teamPlaceholder] = {
                'games': 0,
                'points': 0,
                'diff': 0,
                'scored': 0,
                'obtained': 0,
                'tiepoints': 0,
            }

        if tiepoints > 0:
            self.GroupResults[teamPlaceholder]['tiepoints'] += tiepoints

        elif (points != None):
            self.GroupResults[teamPlaceholder]['games'] += 1
            self.GroupResults[teamPlaceholder]['points'] += points
            self.GroupResults[teamPlaceholder]['scored'] += scored
            self.GroupResults[teamPlaceholder]['obtained'] += obtained
            self.GroupResults[teamPlaceholder]['diff'] += scored - obtained

    def FillRanks(self):
        """ vyplnime tymy v group ranks podle poradi"""
        rank = 1
        # projdeme tymy podle poradi
        for tph in self.Results.keys():
            # do tph v grouprank doplnime tym dle poradi
            rankTph = self.grouprank_set.get(rank=rank).teamPlaceholder
            rankTph.team = tph.team
            rankTph.save()
            # skocime na dalsi tym v poradi
            rank += 1

        # na skupine nastavime priznak finished
        self.finished = True
        self.save()

    @property
    def LastSchedule(self):
        """ Najde posledni schedule k dane group """
        # zkusime posledni vygenerovany match
        last_schedule = Match.objects.filter(group=self).last().schedule_set.last()

        for m in Match.objects.filter(group=self):
            # pokud je zapas pozdeji, ulozime si ho
            if m.schedule_set.last().time > last_schedule.time:
                last_schedule = m.schedule_set.last()

        return last_schedule

    @property
    def NeedsWinner(self):
        """ zapasy ve skupine potrebuji viteze"""
        return self.teams == 2
