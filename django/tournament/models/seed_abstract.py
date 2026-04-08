from django.db import models


class SeedAbstract(models.Model):
    rank = models.PositiveSmallIntegerField()
    teamPlaceholder = models.ForeignKey('TeamPlaceholder', null=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True
