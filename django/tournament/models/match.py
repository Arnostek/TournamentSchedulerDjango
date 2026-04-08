from django.db import models


class Match(models.Model):
    division = models.ForeignKey('Division', on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    phase_block = models.PositiveSmallIntegerField()
    home = models.ForeignKey('TeamPlaceholder', related_name='home_matches', on_delete=models.CASCADE)
    away = models.ForeignKey('TeamPlaceholder', related_name='away_matches', on_delete=models.CASCADE)
    referee = models.ForeignKey('TeamPlaceholder', null=True, blank=True, related_name='referee_matches', on_delete=models.CASCADE)
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)

    @property
    def home_points(self):
        return self.get_points(self.home_score, self.away_score)

    @property
    def away_points(self):
        return self.get_points(self.away_score, self.home_score)

    def tph_obtained(self, tph):
        """ vraci obtained z pohledu tph"""
        # pokud je tph home
        if tph == self.home:
            return self.away_score
        # pokud je tph away
        if tph == self.away:
            return self.home_score
        # default
        return None

    def tph_scored(self, tph):
        """ vraci scored z pohledu tph"""
        # pokud je tph home
        if tph == self.home:
            return self.home_score
        # pokud je tph away
        if tph == self.away:
            return self.away_score
        # default
        return None

    def tph_points(self, tph):
        """ vraci points z pohledu tph"""
        # pokud je tph home
        if tph == self.home:
            return self.home_points
        # pokud je tph away
        if tph == self.away:
            return self.away_points
        # default
        return None

    @property
    def score_filled(self):
        if (self.home_score == None) or (self.away_score == None):
            return False
        else:
            return True

    def get_points(self, me, oponent):
        """ pocet bodu v zavislosti na score zapasu"""
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
        return "Match {} group {} ({})".format(self.division.name, self.group.name, self.id)