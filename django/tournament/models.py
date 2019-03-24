from django.db import models

# Create your models here.

class Tournament(models.Model):
    name = models.CharField(max_length = 200)
    slug = models.SlugField()

class Division(models.Model):
    name = models.CharField(max_length = 200)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

class Group(models.Model):
    name = models.CharField(max_length = 200)
    tournament = models.ForeignKey(Division, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)

class Team(models.Model):
    name = models.CharField(max_length = 200)

class Match(models.Model):
    home = models.ForeignKey(Team, related_name = 'home_matches', on_delete=models.CASCADE)
    away = models.ForeignKey(Team, related_name = 'away_matches', on_delete=models.CASCADE)
    referee = models.ForeignKey(Team, related_name = 'referee_matches', on_delete=models.CASCADE)
