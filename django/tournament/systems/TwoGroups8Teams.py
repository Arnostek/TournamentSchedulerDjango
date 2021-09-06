from .DivisionSystemBase import DivisionSystemBase

class TwoGroups8Teams(DivisionSystemBase):
    """ Two groups, Lower and Higher group, finals"""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(TwoGroups8Teams, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - first round
        phase = 1
        self.division.CreateGroups(['A','B'], self.division.seed_placeholders, phase, ['B','A'])

        # phase 2 - second round
        phase += 1

        a_ranks = self.division.GetGroupsRanks(['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])

        self.division.CreateGroups(['C','D'], [a_ranks[0],a_ranks[2],b_ranks[2],b_ranks[0],a_ranks[1],a_ranks[3],b_ranks[3],b_ranks[1]], phase, ['D','C'])

        # places
        # 7th
        phase += 1
        self.division.CreateGroups(['7th'], self.division.GetGroupsRanks(['D'])[2:4], phase)

        # 5th
        self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['D'])[0:2], phase)

        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['C'])[2:4], phase)

        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['C'])[0:2], phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.division.GetGroupsRanks(['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])
        c_ranks = self.division.GetGroupsRanks(['C'])
        d_ranks = self.division.GetGroupsRanks(['D'])

        self._GroupAddReferees('7th', [d_ranks[1]])
        self._GroupAddReferees('5th', [d_ranks[2]])

        self._GroupAddReferees('3rd',[d_ranks[0]])
        self._GroupAddReferees('final',[c_ranks[2]])
