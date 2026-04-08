from django.db import models
import datetime


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def CreatePitches(self, num):
        for pn in range(num):
            self.pitch_set.create(name='Pitch {}'.format(pn + 1))

    def CreateSchedules(self, begin, end, gametime=30):
        time = begin
        delta = datetime.timedelta(minutes=gametime)
        gn = self.schedule_set.count() + 1
        while time < end:
            for pitch in self.pitch_set.all():
                self.schedule_set.create(tournament=self, time=time, pitch=pitch, game_number=gn)
                gn += 1
            time += delta

    def __str__(self):
        return self.name


class Pitch(models.Model):
    name = models.CharField(max_length=50)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    time = models.DateTimeField()
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE)
    game_number = models.PositiveSmallIntegerField(null=True)
    match = models.ForeignKey('Match', null=True, on_delete=models.SET_NULL)