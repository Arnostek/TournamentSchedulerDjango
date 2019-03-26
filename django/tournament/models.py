from django.db import models

#
class Tournament(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.SlugField()

class Division(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.SlugField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

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

# seed
class DivisionSeed(models.Model):
    rank = models.PositiveSmallIntegerField()
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    teamPlaceholder = models.ForeignKey(TeamPlaceholder, on_delete=models.CASCADE)

class DivisionRank(DivisionSeed):
    pass

class GroupSeed(models.Model):
    rank = models.PositiveSmallIntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    teamPlaceholder = models.ForeignKey(TeamPlaceholder, on_delete=models.CASCADE)

class GroupRank(GroupSeed):
    pass

    # seed ?

class Match(models.Model):
    home = models.ForeignKey(TeamPlaceholder, related_name = 'home_matches', on_delete=models.CASCADE)
    away = models.ForeignKey(TeamPlaceholder, related_name = 'away_matches', on_delete=models.CASCADE)
    referee = models.ForeignKey(TeamPlaceholder, related_name = 'referee_matches', on_delete=models.CASCADE)
