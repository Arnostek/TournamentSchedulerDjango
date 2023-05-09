from .DivisionSystemBase import DivisionSystemBase
from tournament.models import GroupPointsTransfer
import random

class SingleGroup2Rounds(DivisionSystemBase):
    """ Jedna zakladni skupina, kazdy s kazdym, zapas o 3. a prvni misto """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(SingleGroup2Rounds, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # create game system
        self._createSystem()
        # generate matches
        self._createMatches()
        # add referees
        self._addReferees()

    def _createSystem(self):
        # phase 1 - first round
        phase = 1
        self.division.CreateGroups(['R1'], self.division.seed_placeholders, phase, referee_groups = ['R1'])
        # phase 2 - second round
        phase += 1
        self.division.CreateGroups(['R2'], self.division.seed_placeholders, phase, referee_groups = ['R2'])
        r2_ranks = self.division.GetGroupsRanks(['R2'])
        # transfer points from R1 to R2
        GroupPointsTransfer.objects.create(src = self.division.GetGroup('R1'), dest = self.division.GetGroup('R2'))
        # 3rd
        if self.teams_count > 3:
            phase += 1
            a_ranks = r2_ranks
            self.division.CreateGroups(['3rd'], [r2_ranks[2], r2_ranks[3]] , phase)
        # final
        phase += 1
        self.division.CreateGroups(['final'],[r2_ranks[0], r2_ranks[1]] , phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        r2_ranks = self.division.GetGroupsRanks(['R2'])
        self._GroupAddReferees('3rd',[r2_ranks[1]])
        self._GroupAddReferees('final',[r2_ranks[2]])
