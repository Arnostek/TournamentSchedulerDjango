from .DivisionSystemBase import DivisionSystemBase

class TwoGroups8TeamsMiddle(DivisionSystemBase):
    """ Two groups, Cross matches 2nd against 3rd, Lower and Higher group, finals for top 4"""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(TwoGroups8TeamsMiddle, self).__init__(tournament,division_name,division_slug,num_of_teams)
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

        # zapasy 2. vs 3.
        self.division.CreateGroups(['M1','M2'], [a_ranks[1],a_ranks[2],b_ranks[1],b_ranks[2]], phase)

        # phase 3 - druhe kolo
        phase += 1

        # vitezove
        self.division.CreateGroups(['C'], self.division.GetGroupsRanks(['A','B','M1','M2'])[:4],phase, ['C'])
        # porazeni
        self.division.CreateGroups(['D'], self.division.GetGroupsRanks(['M1','M2'])[-2:] + self.division.GetGroupsRanks(['A','B'])[-2:],phase,['D'])

        # umisteni

        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['C'])[2:4], phase)

        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['C'])[0:2], phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        self._GroupAddReferees('M1', self.division.GetGroupsRanks(['A']))
        self._GroupAddReferees('M2', self.division.GetGroupsRanks(['B']))
        #
        # self._GroupAddReferees('7th', self.division.GetGroupsRanks(['S1']))
        # self._GroupAddReferees('5th', self.division.GetGroupsRanks(['S2']))
        #
        # self._GroupAddReferees('3rd',self.division.GetGroupsRanks(['7th']))
        # self._GroupAddReferees('final',self.division.GetGroupsRanks(['5th']))
