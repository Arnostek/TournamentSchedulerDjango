from django.db import models
from django.dispatch import receiver
from .polygon_generator import polygon_generator

#
class Tournament(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.SlugField()

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

    def CreateGroups(self, names, placeholders, phase):
        """ Vytvoreni naseedovanych skupin"""
        #
        groups = []

        # nejdriv zalozime skupiny, objekty si ulozime do groups
        for name in names:
            groups.append(self.group_set.create(name = name, phase = phase))

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
            tph = TeamPlaceholder(name = "{}{}".format(self.name, rank))
            tph.save()
            # zalozim DivisionSeed
            seed = self.grouprank_set.create(rank = rank, teamPlaceholder = tph)

    def CreateMatches(self):
        """ vytvoreni vsech zapasu ve skupine """
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
    referee = models.ForeignKey(TeamPlaceholder, null = True, related_name = 'referee_matches', on_delete=models.CASCADE)
