from django.db import models
from django.dispatch import receiver
from .polygon_generator import polygon_generator
import datetime

#
class Tournament(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.SlugField(unique=True)

    def CreatePitches(self, num):

        for pn in range(num):

            self.pitch_set.create(name = 'Pitch {}'.format(pn+1))

    def CreateSchedules(self, begin, end, gametime = 30):

        time = begin

        delta = datetime.timedelta(minutes = gametime)
        gn = self.schedule_set.count() + 1
        while time < end:
            for pitch in self.pitch_set.all():
                self.schedule_set.create(tournament = self, time = time, pitch = pitch, game_number = gn)
                gn += 1
            time += delta
    def __str__(self):
        return self.name

class Division(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.SlugField()
    teams = models.PositiveSmallIntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return "{} (id={})".format(self.name,self.id)

    def CreateSeeds(self):
        """ Vytvoreni zaznamu division seed"""
        # create SeedDivision
        for rank in range(self.teams):
            rank = rank + 1
            # pripravim si TeamPlaceholder
            tph = TeamPlaceholder(name = "{}_SEED#{:02d}".format(self.slug, rank))
            tph.save()
            # zalozim DivisionSeed
            seed = self.divisionseed_set.create(rank = rank, teamPlaceholder = tph)

    def CreateRanks(self,rank_first,teamPlaceholder_arr):
        """ Vytvoreni zaznamu division rank.
                rank_first: poradi prvniho z listu
                teamPlaceholder_arr: list
        """
        rank = rank_first

        # pokud objekt nejde iterovat, zabalime ho do pole
        if not hasattr(teamPlaceholder_arr, '__iter__'):
            teamPlaceholder_arr = [teamPlaceholder_arr]

        for tph in teamPlaceholder_arr:
            self.divisionrank_set.create(rank = rank, teamPlaceholder = tph)
            rank+=1

    def CreateGroups(self, names, placeholders, phase, referee_groups = None):
        """ Vytvoreni naseedovanych skupin"""
        #
        groups = []

        # nejdriv zalozime skupiny, objekty si ulozime do groups
        for name in names:
            groups.append(self.group_set.create(name = name, phase = phase))

        # pokud jsou referee_groups, priradim je do group
        if referee_groups:
            for rg_index in range(len(referee_groups)):
                rg = groups[rg_index]
                rg.referee_group = self.GetGroup(referee_groups[rg_index])
                rg.save()

        # pak vytvorime a naplnime seedy
        # na zacatek jdeme popredu
        reverse = False
        group_index = 0
        seed_rank = 1

        for tph in placeholders:
            # vytvoreni group seedu
            groups[group_index].groupseed_set.create(rank = seed_rank, teamPlaceholder = tph)
            # podle smeru pridame, nebo ubereme index
            if (reverse):
                # kontrola spodni hranice
                if group_index == 0:
                    reverse = False
                    seed_rank += 1
                else:
                    group_index -= 1
            else:
                # kontrola horni hranice
                if group_index == len(groups) - 1:
                    reverse = True
                    seed_rank += 1
                else:
                    group_index +=1

        # nakonec pro kazdou groupu vytvorime ranks
        for group in groups:
            group.CreateRanks()

    def CreateTeams(self, teams):
        """ Create teams in team placehoders """
        rank = 1

        for team_name in teams:
            # najdu TeamPlaceholder
            tph = self.divisionseed_set.get(rank = rank).teamPlaceholder
            tph.CreateTeam(team_name)

            rank += 1

    @property
    def seed_placeholders(self):
        """
        vraci list naseedovanych tymu divize serazeny podle rank
        """
        return [seed.teamPlaceholder for seed in self.divisionseed_set.order_by('rank')]

    def GetGroupsRanks(self,group_names):
        """
        vraci list team placeholderu z vybranych Group
        """
        groups = self.group_set.filter(name__in = group_names)
        ranks = GroupRank.objects.filter(group__in = groups).order_by('rank','group_id')
        return [rank.teamPlaceholder for rank in ranks]

    def GetGroup(self,group_name):
        """
        vraci group podle jmena
        """
        return self.group_set.get(name = group_name)

    def find_rank(self,group_name,rank):
        """ Hledani tymu podle groupy a poradi"""
        group = self.group_set.get(name = group_name)
        rank = group.grouprank_set.get(rank = rank)
        return rank.teamPlaceholder

    def CreateMatches(self):
        """ Vytvoreni matchu pro divizi """
        for group in self.group_set.all():
            group.CreateMatches()

@receiver(models.signals.post_save, sender=Division)
def division__after_create(sender, instance, created, *args, **kwargs):
    if created:
        instance.CreateSeeds()

class Group(models.Model):
    name = models.CharField(max_length = 200)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    phase = models.PositiveSmallIntegerField()
    finished = models.BooleanField(default=False)
    referee_group = models.ForeignKey("self", null = True,on_delete=models.CASCADE)

    def __str__(self):
        return "{} (id={})".format(self.name,self.id)

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
                wl = ['Winner','Loser']
                tph.name = "{} {}".format(wl[rank-1],self.name)
            else:
                tph.name = "{}. gr {}".format(rank,self.name)
            tph.save()
            # zalozim DivisionSeed
            seed = self.grouprank_set.create(rank = rank, teamPlaceholder = tph)

    def CreateMatches(self):
        """ vytvoreni vsech zapasu ve skupine """
        # pokud jeste neexistuje zadny zapas
        if self.match_set.count() == 0:
            for zapas_tup in polygon_generator(self.teams):
                self.CreateMatch(zapas_tup)

    def CreateMatch(self,zapas_tup):
        """ Vytvoreni jednoho zapasu podle poradi seedu """
        self.match_set.create(
            division = self.division,
            group = self,
            phase_block = zapas_tup[2],
            home = self.groupseed_set.get(rank = zapas_tup[0]).teamPlaceholder,
            away = self.groupseed_set.get(rank = zapas_tup[1]).teamPlaceholder,
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
            for old_tph,old_result in gpt.src.Results.items():
                # najdeme novy groupseed podle tymu
                new_gs_set = self.groupseed_set.filter(teamPlaceholder__team = old_tph.team)
                # pokud tym najdeme, pripocteme vysledky
                if len(new_gs_set) > 0:
                    self.AddTeamResult(
                            new_gs_set[0].teamPlaceholder,
                            old_result["points"],
                            old_result["scored"],
                            old_result["obtained"])
                    # doplnime pocet zapasu
                    for i in range(old_result["games"]-1):
                        self.AddTeamResult(new_gs_set[0].teamPlaceholder,0,0,0)

        # pokud existuji, pricteme body z GroupTieRankingPoints
        for erp in self.grouptierankingpoints_set.all():
            self.AddTeamResult(erp.tph, None, None, None, erp.tiepoints)

        # setridene dle poradi
        tmp =  sorted(
            self.GroupResults.items(),
            key = lambda item : (
                    int(item[1]['points']),
                    int(item[1]['diff']),
                    int(item[1]['scored']),
                    int(item[1]['tiepoints']),
            ),
            reverse = True
        )
        # vracime v puvodni strukture
        return { tup[0] : tup[1] for tup in tmp}

    @property
    def ResultsDetail(self):
        """ Data pro cross tabulku zapasu"""
        import pandas as pd

        # seznam tph z groupy bereme z results - setridene dle poradi
        teams = [tph for tph in self.Results.keys()]
        # dataframe tabulky
        df = pd.DataFrame(index=teams,columns=teams)

        # naplneni zapasu
        for match in self.match_set.all():
            df.loc[match.home,match.away] = match
            df.loc[match.away,match.home] = match

        # df pro vysledky
        results = pd.DataFrame(index=df.index, columns=['Games','Points','Diff','Scored','Obtained','TiePoints','Rank'])

        # vysledky zapasu
        matches = pd.DataFrame(index=df.index,columns=df.columns)

        # napocteni bodu a vysledku
        for tph in df.index:

            # vysledky prebirame ze stare metody -
            results.loc[tph,'Games'] = self.Results[tph]['games']
            results.loc[tph,'Points'] = self.Results[tph]['points']
            results.loc[tph,'Scored'] = self.Results[tph]['scored']
            results.loc[tph,'Obtained'] = self.Results[tph]['obtained']
            results.loc[tph,'TiePoints'] = self.Results[tph]['tiepoints']

            for tph_col in df.columns:

                m = df.loc[tph,tph_col]
                if isinstance(m,Match):
                    if m.score_filled:
                        matches.loc[tph,tph_col] = '{} : {}'.format(m.tph_scored(tph),m.tph_obtained(tph))
                    else:
                        matches.loc[tph,tph_col] = ' : '
                else:
                    matches.loc[tph,tph_col] = 'X'

        results['Diff'] = results['Scored'] - results['Obtained']
        # rank - setridime index a naplnime Rank
        rank_cols = ['Points','Diff','Scored','TiePoints']
        # results.loc[results.sort_values(by=rank_cols,ascending=False).index,'Rank'] = range(1,len(results)+1)
        results['Rank'] = results.sort_values(by=rank_cols,ascending=False).groupby(rank_cols, sort=False).ngroup()+1
        # vse prevedeme na int
        results = results.astype(int)

        # join df
        matches = matches.join(results)

        # upravime indexy a columns
        matches.index = matches.index.map(lambda t: t.team_name)
        matches.columns = matches.columns.map(lambda t: t.team_name if isinstance(t,TeamPlaceholder) else t)

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

    def AddTeamResult(self, teamPlaceholder, points, scored, obtained, tiepoints = 0):
        """ Pripocteni bodu pro jeden tym"""

        if teamPlaceholder not in self.GroupResults:
            self.GroupResults[teamPlaceholder] = {
            'games' : 0,
            'points' : 0,
            'diff' : 0,
            'scored' : 0,
            'obtained' : 0,
            'tiepoints' : 0,
            }

        if tiepoints > 0:
            self.GroupResults[teamPlaceholder]['tiepoints'] += tiepoints

        elif (points != None):
            self.GroupResults[teamPlaceholder]['games'] +=  1
            self.GroupResults[teamPlaceholder]['points'] +=  points
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
        last_schedule = Match.objects.filter(group = self).last().schedule_set.last()

        for m in Match.objects.filter(group = self):
            # pokud je zapas pozdeji, ulozime si ho
            if m.schedule_set.last().time > last_schedule.time:
                last_schedule = m.schedule_set.last()

        return last_schedule

    @property
    def NeedsWinner(self):
        """ zapasy ve skupine potrebuji viteze"""
        return self.teams == 2

class GroupPointsTransfer(models.Model):
    """ Prenaseni bodu mezi skupinami """
    src = models.ForeignKey(Group, on_delete=models.CASCADE, related_name = "points_transfer_src")
    dest = models.ForeignKey(Group, on_delete=models.CASCADE, related_name = "points_transfer_dst")

# teams
class Team(models.Model):
    name = models.CharField(max_length = 200)
#    division = models.ForeignKey(Division, on_delete=models.CASCADE)

class TeamPlaceholder(models.Model):
    name = models.CharField(max_length = 200)
#    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null = True, on_delete=models.PROTECT)

    def CreateTeam(self,team_name):
        """ create related team record """
        if self.team:
            raise("Team record already exists!")
        else:
            t = Team(name = team_name)
            t.save()
            self.team = t
            self.save()

    @property
    def team_name(self):
        """ Returns team or team placehoder name"""
        if (self.team):
            return self.team.name
        else:
            return self.name

    def __str__(self):
        return self.team_name + ' ('+self.name+')'

class GroupTieRankingPoints(models.Model):
    """ extra body v pripade shody ve skupine"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    tph = models.ForeignKey(TeamPlaceholder, on_delete=models.CASCADE)
    tiepoints = models.PositiveSmallIntegerField()

# seed tables
class SeedAbstract(models.Model):
    rank = models.PositiveSmallIntegerField()
    teamPlaceholder = models.ForeignKey(TeamPlaceholder, null = True, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class DivisionSeed(SeedAbstract):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)

class DivisionRank(SeedAbstract):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)

class GroupSeed(SeedAbstract):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class GroupRank(SeedAbstract):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    # seed ?

class Match(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    phase_block = models.PositiveSmallIntegerField()
    home = models.ForeignKey(TeamPlaceholder, related_name = 'home_matches', on_delete=models.CASCADE)
    away = models.ForeignKey(TeamPlaceholder, related_name = 'away_matches', on_delete=models.CASCADE)
    referee = models.ForeignKey(TeamPlaceholder, null = True, blank=True, related_name = 'referee_matches', on_delete=models.CASCADE)
    home_score = models.PositiveSmallIntegerField(null = True, blank=True)
    away_score = models.PositiveSmallIntegerField(null = True, blank=True)

    @property
    def home_points(self):
        return self.get_points(self.home_score,self.away_score)

    @property
    def away_points(self):
        return self.get_points(self.away_score,self.home_score)

    def tph_obtained(self,tph):
        """ vraci obtained z pohledu tph"""
        # pokud je tph home
        if tph == self.home:
            return self.away_score
        # pokud je tph away
        if tph == self.away:
            return self.home_score
        # default
        return None

    def tph_scored(self,tph):
        """ vraci scored z pohledu tph"""
        # pokud je tph home
        if tph == self.home:
            return self.home_score
        # pokud je tph away
        if tph == self.away:
            return self.away_score
        # default
        return None

    def tph_points(self,tph):
        """ vraci points z pohledu tph"""
        # pokud je tph home
        if tph == self.home:
            return self.home_points
        # pokud je tph away
        if tph == self.away:
            return self.away_points
        # default
        return None

    @property
    def score_filled(self):
        if (self.home_score == None) or (self.away_score == None):
            return False
        else:
            return True

    def get_points(self,me,oponent):
        """ pocet bodu v zavislosti na score zapasu"""
        if (me == None) or (oponent == None):
            return None
        # vitezstvi 3 body
        if me > oponent:
            return 3
        # remiza 1 bod
        elif me == oponent:
            return 1
        # prohra 0 bodu
        else:
            return 0
    @property
    def locked(self):
        """ zapas je zamcen, nemuzeme menit score """
        # grupa je uzavrena
        if self.group.finished:
            return True
        # neni vyplnen home, nebo away team
        if not self.home.team:
            return True
        if not self.away.team:
            return True
        # pokud jsme na nic nenarazili, score je mozno editovat
        return False

    def __str__(self):
        return "Match {} group {} ({})".format(self.division.name,self.group.name,self.id)


class Pitch(models.Model):
    name = models.CharField(max_length = 50)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Schedule(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    time = models.DateTimeField()
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE)
    game_number = models.PositiveSmallIntegerField(null = True)
    match = models.ForeignKey(Match, null = True, on_delete=models.SET_NULL)
