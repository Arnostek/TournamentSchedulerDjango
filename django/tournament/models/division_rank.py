from django.db import models
from .seed_abstract import SeedAbstract


class DivisionRank(SeedAbstract):
    division = models.ForeignKey('Division', on_delete=models.CASCADE)
