from django.db import models
from django.dispatch import receiver
from .team_placeholder import TeamPlaceholder
from .group_rank import GroupRank


class Division(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    teams = models.PositiveSmallIntegerField()
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)

    def __str__(self):
        return "{} (id={})".format(self.name, self.id)

    def CreateSeeds(self):
        """ Vytvoreni zaznamu division seed"""
        # create SeedDivision
        for rank in range(self.teams):
            rank = rank + 1
            # pripravim si TeamPlaceholder
            tph = TeamPlaceholder(name="{}_SEED#{:02d}".format(self.slug, rank))
            tph.save()
            # zalozim DivisionSeed
            seed = self.divisionseed_set.create(rank=rank, teamPlaceholder=tph)

    def CreateRanks(self, rank_first, teamPlaceholder_arr):
        """ Vytvoreni zaznamu division rank.
                rank_first: poradi prvniho z listu
                teamPlaceholder_arr: list
        """
        rank = rank_first

        # pokud objekt nejde iterovat, zabalime ho do pole
        if not hasattr(teamPlaceholder_arr, '__iter__'):
            teamPlaceholder_arr = [teamPlaceholder_arr]

        for tph in teamPlaceholder_arr:
            self.divisionrank_set.create(rank=rank, teamPlaceholder=tph)
            rank += 1

    def CreateGroups(self, names, placeholders, phase, referee_groups=None):
        """ Vytvoreni naseedovanych skupin"""
        #
        groups = []

        # nejdriv zalozime skupiny, objekty si ulozime do groups
        for name in names:
            groups.append(self.group_set.create(name=name, phase=phase))

        # pokud jsou referee_groups, priradim je do group
        if referee_groups:
            for rg_index in range(len(referee_groups)):
                rg = groups[rg_index]
                rg.referee_group = self.GetGroup(referee_groups[rg_index])
                rg.save()

        # pak vytvorime a naplnime seedy
        # na zacatek jdeme popredu
        reverse = False
        group_index = 0
        seed_rank = 1

        for tph in placeholders:
            # vytvoreni group seedu
            groups[group_index].groupseed_set.create(rank=seed_rank, teamPlaceholder=tph)
            # podle smeru pridame, nebo ubereme index
            if (reverse):
                # kontrola spodni hranice
                if group_index == 0:
                    reverse = False
                    seed_rank += 1
                else:
                    group_index -= 1
            else:
                # kontrola horni hranice
                if group_index == len(groups) - 1:
                    reverse = True
                    seed_rank += 1
                else:
                    group_index += 1

        # nakonec pro kazdou groupu vytvorime ranks
        for group in groups:
            group.CreateRanks()

    def CreateTeams(self, teams):
        """ Create teams in team placehoders """
        rank = 1

        for team_name in teams:
            # najdu TeamPlaceholder
            tph = self.divisionseed_set.get(rank=rank).teamPlaceholder
            tph.CreateTeam(team_name)

            rank += 1

    @property
    def seed_placeholders(self):
        """
        vraci list naseedovanych tymu divize serazeny podle rank
        """
        return [seed.teamPlaceholder for seed in self.divisionseed_set.order_by('rank')]

    def GetGroupsRanks(self, group_names):
        """
        vraci list team placeholderu z vybranych Group
        """
        groups = self.group_set.filter(name__in=group_names)
        ranks = GroupRank.objects.filter(group__in=groups).order_by('rank', 'group_id')
        return [rank.teamPlaceholder for rank in ranks]

    def GetGroup(self, group_name):
        """
        vraci group podle jmena
        """
        return self.group_set.get(name=group_name)

    def find_rank(self, group_name, rank):
        """ Hledani tymu podle groupy a poradi"""
        group = self.group_set.get(name=group_name)
        rank = group.grouprank_set.get(rank=rank)
        return rank.teamPlaceholder

    def CreateMatches(self):
        """ Vytvoreni matchu pro divizi """
        for group in self.group_set.all():
            group.CreateMatches()


@receiver(models.signals.post_save, sender=Division)
def division__after_create(sender, instance, created, *args, **kwargs):
    if created:
        instance.CreateSeeds()
