from .DivisionSystemBase import DivisionSystemBase

class TwoGroups8Teams(DivisionSystemBase):
    """ Two groups in two rounds, finals"""

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
        # a_ranks = self.division.GetGroupsRanks(['A'])

        # phase 2 - second round
        phase += 1
        self.division.CreateGroups(['C','D'], self.division.GetGroupsRanks(['C','D']), phase, ['D','C'])
        # a_ranks = self.division.GetGroupsRanks(['A'])

        # phase 3 - places
        phase += 1
        mista = [m for m in range(5,self.teams_count,2)]
        mista.reverse()
        for misto in mista:
            self.division.CreateGroups(['{}th'.format(misto)], self.division.GetGroupsRanks(['C','D'])[misto - 1: misto + 1], phase)

        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['C','D'])[2:4], phase)

        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['C','D'])[0:2], phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.division.GetGroupsRanks(['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])
        c_ranks = self.division.GetGroupsRanks(['C'])
        d_ranks = self.division.GetGroupsRanks(['D'])

        self._GroupAddReferees('7th', [c_ranks[1]])
        self._GroupAddReferees('5th', [d_ranks[0]])

        self._GroupAddReferees('3rd',[self.division.GetGroupsRanks(['7th'])[0]])
        self._GroupAddReferees('final',[self.division.GetGroupsRanks(['5th'])[0]])
