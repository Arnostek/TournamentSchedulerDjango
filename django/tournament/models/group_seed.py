from django.db import models
from .seed_abstract import SeedAbstract


class GroupSeed(SeedAbstract):
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
