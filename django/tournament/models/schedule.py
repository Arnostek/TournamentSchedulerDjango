from django.db import models


class Schedule(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    time = models.DateTimeField()
    pitch = models.ForeignKey('Pitch', on_delete=models.CASCADE)
    game_number = models.PositiveSmallIntegerField(null=True)
    match = models.ForeignKey('Match', null=True, on_delete=models.SET_NULL)
