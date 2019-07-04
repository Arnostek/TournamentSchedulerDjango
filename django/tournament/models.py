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

        # setridene dle poradi
        tmp =  sorted(
            self.GroupResults.items(),
            key = lambda item : (
                    int(item[1]['points']),
                    int(item[1]['diff']),
                    int(item[1]['scored']),
            ),
            reverse = True
        )
        # vracime v puvodni strukture
        return { tup[0] : tup[1] for tup in tmp}



    @property
    def All_scores_filled(self):
        """ Jsou uz zadana score ze vsech zapasu skupiny? """

        for match in self.match_set.all():
            if not match.score_filled:
                return False

        return True

    def AddTeamResult(self, teamPlaceholder, points, scored, obtained):
        """ Pripocteni bodu pro jeden tym"""

        if teamPlaceholder not in self.GroupResults:
            self.GroupResults[teamPlaceholder] = {
            'games' : 0,
            'points' : 0,
            'diff' : 0,
            'scored' : 0,
            'obtained' : 0,
            }

        if (points != None):
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

    @property
    def score_filled(self):
        if (self.home_score == None) or (self.away_score == None):
            return False
        else:
            return True

    def get_points(self,me,oponent):
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
