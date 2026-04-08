from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=200)
#    division = models.ForeignKey(Division, on_delete=models.CASCADE)


class TeamPlaceholder(models.Model):
    name = models.CharField(max_length=200)
#    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null=True, on_delete=models.PROTECT)

    def CreateTeam(self, team_name):
        """ create related team record """
        if self.team:
            raise ("Team record already exists!")
        else:
            t = Team(name=team_name)
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
        return self.team_name + ' (' + self.name + ')'