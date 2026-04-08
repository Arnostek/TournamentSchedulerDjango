from django.db import models


class Pitch(models.Model):
    name = models.CharField(max_length=50)
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
