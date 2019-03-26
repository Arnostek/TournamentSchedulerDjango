from django.db import models
from django.dispatch import receiver

#
class Tournament(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.SlugField()

class Division(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.SlugField()
    teams = models.PositiveSmallIntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def CreateSeeds(self):
        # create SeedDivision
        for rank in range(self.teams):
            rank = rank + 1
            # pripravim si TeamPlaceholder
            tph = TeamPlaceholder(name = "{}_SEED#{:02d}".format(self.slug, rank))
            tph.save()
            # zalozim DivisionSeed
            seed = self.divisionseed_set.create(rank = rank, teamPlaceholder = tph)

    def CreateGroups(self,names,placeholders):
        """ Vytvoreni naseedovanych skupin"""
        #
        groups = []

        # nejdriv zalozime skupiny, objekty si ulozime do groups
        for name in names:
            groups.append(self.group_set.create(name = name))

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

@receiver(models.signals.post_save, sender=Division)
def division__after_create(sender, instance, created, *args, **kwargs):
    if created:
        instance.CreateSeeds()

class Group(models.Model):
    name = models.CharField(max_length = 200)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)

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

# teams
class Team(models.Model):
    name = models.CharField(max_length = 200)
#    division = models.ForeignKey(Division, on_delete=models.CASCADE)

class TeamPlaceholder(models.Model):
    name = models.CharField(max_length = 200)
#    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null = True, on_delete=models.PROTECT)

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

class DivisionRank(DivisionSeed):
    pass

class GroupSeed(SeedAbstract):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class GroupRank(GroupSeed):
    pass

    # seed ?

class Match(models.Model):
    home = models.ForeignKey(TeamPlaceholder, related_name = 'home_matches', on_delete=models.CASCADE)
    away = models.ForeignKey(TeamPlaceholder, related_name = 'away_matches', on_delete=models.CASCADE)
    referee = models.ForeignKey(TeamPlaceholder, related_name = 'referee_matches', on_delete=models.CASCADE)
