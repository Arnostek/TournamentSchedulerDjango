from .DivisionSystemBase import DivisionSystemBase

class TwoGroups8TeamsCross(DivisionSystemBase):
    """ Two groups, Lower and Higher group, finals"""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(TwoGroups8TeamsCross, self).__init__(tournament,division_name,division_slug,num_of_teams)
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

        # phase 2 - Krizove zapasy
        phase += 1

        a_ranks = self.division.GetGroupsRanks(['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])

        # zapasy 1. vs 4. a 2. vs 3.
        self.division.CreateGroups(['C1','C2','C3','C4'], [a_ranks[0],a_ranks[1],a_ranks[2],a_ranks[3],b_ranks[0],b_ranks[1],b_ranks[2],b_ranks[3]], phase, ['C3','C4','C1','C2'])

        # phase 3 - semi
        phase += 1
        # vitezove
        self.division.CreateGroups(['S1','S2'], self.division.GetGroupsRanks(['C1','C2','C3','C4'])[:4],phase)
        # porazeni
        self.division.CreateGroups(['S3','S4'], self.division.GetGroupsRanks(['C1','C2','C3','C4'])[-4:],phase,['S1','S2'])

        # umisteni
        # 7th, 5th
        phase += 1
        self.division.CreateGroups(['7th'], self.division.GetGroupsRanks(['S3','S4'])[2:4], phase)
        self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['S3','S4'])[0:2], phase)

        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['S1','S2'])[2:4], phase)

        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['S1','S2'])[0:2], phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.division.GetGroupsRanks(['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])

        self._GroupAddReferees('S1', self.division.GetGroupsRanks(['C3'])[-1:])
        self._GroupAddReferees('S2', self.division.GetGroupsRanks(['C2'])[-1:])

        self._GroupAddReferees('7th', self.division.GetGroupsRanks(['S1']))
        self._GroupAddReferees('5th', self.division.GetGroupsRanks(['S2']))

        self._GroupAddReferees('3rd',self.division.GetGroupsRanks(['7th']))
        self._GroupAddReferees('final',self.division.GetGroupsRanks(['5th']))
