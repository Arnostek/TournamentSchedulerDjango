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

    def CreateSeed(self):

        # create SeedDivision
        for rank in range(self.teams):
            rank = rank + 1
            # pripravim si TeamPlaceholder
            tph = TeamPlaceholder(name = "{}_SEED#{:02d}".format(self.slug, rank))
            tph.save()
            # zalozim DivisionSeed
            seed = self.divisionseed_set.create(rank = rank, teamPlaceholder = tph)


@receiver(models.signals.post_save, sender=Division)
def division__after_create(sender, instance, created, *args, **kwargs):
    if created:
        instance.CreateSeed()

class Group(models.Model):
    name = models.CharField(max_length = 200)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)

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
