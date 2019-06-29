from .DivisionSystemBase import DivisionSystemBase
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
        self.division.CreateGroups(['R1'], self.division.seed_placeholders, phase, ['R1'])
        r1_ranks = self.division.GetGroupsRanks(['R1'])
        # phase 2 - second round
        phase += 1
        self.division.CreateGroups(['R2'], self.division.seed_placeholders, phase, ['R2'])
        r2_ranks = self.division.GetGroupsRanks(['R2'])
        # 3rd
        phase += 1
        a_ranks = r2_ranks
        self.division.CreateGroups(['3rd'], [a_ranks[2], a_ranks[3]] , phase)
        # final
        phase += 1
        self.division.CreateGroups(['final'],[a_ranks[0], a_ranks[1]] , phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.division.GetGroupsRanks(['A'])
        if len(a_ranks) > 5:
            self._GroupAddReferees('3rd',[a_ranks[5]])
        if len(a_ranks) > 4:
            self._GroupAddReferees('final',[a_ranks[4]])