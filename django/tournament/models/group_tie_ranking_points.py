from django.db import models


class GroupTieRankingPoints(models.Model):
    """ extra body v pripade shody ve skupine"""
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    tph = models.ForeignKey('TeamPlaceholder', on_delete=models.CASCADE)
    tiepoints = models.PositiveSmallIntegerField()
