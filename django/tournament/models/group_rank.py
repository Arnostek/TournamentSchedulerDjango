from django.db import models
from .seed_abstract import SeedAbstract


class GroupRank(SeedAbstract):
    group = models.ForeignKey('Group', on_delete=models.CASCADE)

    # seed ?
