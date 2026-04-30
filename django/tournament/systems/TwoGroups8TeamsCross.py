from .DivisionSystemBase import DivisionSystemBase

class TwoGroups8TeamsCross(DivisionSystemBase):
    """ Two groups, 4 semifinals, finals"""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(TwoGroups8TeamsCross, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True,semi5_8 = True)
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
        self.division.CreateGroups(['QF1','QF2','QF3','QF4'], [a_ranks[0],a_ranks[1],a_ranks[2],a_ranks[3],b_ranks[0],b_ranks[1],b_ranks[2],b_ranks[3]], phase)

        # phase 3 - semi
        phase += 1
        # vitezove
        self.division.CreateGroups(['SF1','SF2'], self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[:4],phase)
        # porazeni
        self.division.CreateGroups(['SF3','SF4'], self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[-4:],phase)

        # umisteni
        # 7th, 5th
        phase += 1
        self.division.CreateGroups(['7th'], self.division.GetGroupsRanks(['SF3','SF4'])[2:4], phase)
        self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['SF3','SF4'])[0:2], phase)

        # 3rd
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SF1','SF2'])[2:4], phase)

        # final
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['SF1','SF2'])[0:2], phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.division.GetGroupsRanks(['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])

        self._GroupAddReferees('QF1', [self.division.GetGroupsRanks(['B'])[1]])
        self._GroupAddReferees('QF2', [self.division.GetGroupsRanks(['B'])[0]])
        self._GroupAddReferees('QF3', [self.division.GetGroupsRanks(['A'])[0]])
        self._GroupAddReferees('QF4', [self.division.GetGroupsRanks(['A'])[1]])


        self._GroupAddReferees('SF1', self.division.GetGroupsRanks(['QF1']))
        self._GroupAddReferees('SF2', self.division.GetGroupsRanks(['QF2']))
        self._GroupAddReferees('SF3', self.division.GetGroupsRanks(['QF3']))
        self._GroupAddReferees('SF4', self.division.GetGroupsRanks(['QF4']))

        self._GroupAddReferees('7th', self.division.GetGroupsRanks(['SF1']))
        self._GroupAddReferees('5th', self.division.GetGroupsRanks(['SF2']))

        self._GroupAddReferees('3rd',self.division.GetGroupsRanks(['SF4']))
        self._GroupAddReferees('final',self.division.GetGroupsRanks(['SF3']))
