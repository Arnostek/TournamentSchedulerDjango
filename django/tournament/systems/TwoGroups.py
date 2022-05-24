from .DivisionSystemBase import DivisionSystemBase

class TwoGroups(DivisionSystemBase):
    """ Dve zakladni skupiny, semi pro 1. a 2., zapasy o misto """

    def __init__(self,tournament,division_name,division_slug,num_of_teams,last3=False,semi5_8=False):
        # zavolam konsturktor Predka
        super(TwoGroups, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # lichy pocet tymu?
        self.last3 = last3
        # semi pro 5-8
        self.semi5_8 = semi5_8
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - zakladni skupina
        phase = 1
        self.division.CreateGroups(['A','B'], self.division.seed_placeholders, phase, ['B','A'])
        # a_ranks = self.division.GetGroupsRanks(['A'])

        # prvni 4 tymy jdou do semi
        phase += 1
        self.division.CreateGroups(['SemiA','SemiB'], self.division.GetGroupsRanks(['A','B'])[:4], phase)
        # volitelne semi pro 5-8
        if self.semi5_8:
            self.division.CreateGroups(['SemiC','SemiD'], self.division.GetGroupsRanks(['A','B'])[4:8], phase)
        # lichy pocet tymu = skupina poslednich tri
        if self.last3:
            self.division.CreateGroups(['Last3'], self.division.GetGroupsRanks(['A','B'])[-3:], phase)
        # zapasy o mista
        phase += 1
        if self.semi5_8:
            mista = [m for m in range(9,self.teams_count if not self.last3 else self.teams_count - 3,2)]
        else:
            mista = [m for m in range(5,self.teams_count if not self.last3 else self.teams_count - 3,2)]
        # mista = [m for m in range(5,self.teams_count,2)]
        mista.reverse()
        for misto in mista:
            self.division.CreateGroups(['{}th'.format(misto)], self.division.GetGroupsRanks(['A','B'])[misto - 1: misto + 1], phase)

        if self.semi5_8:
            self.division.CreateGroups(['7th'], self.division.GetGroupsRanks(['SemiC','SemiD'])[2:4], phase)
            self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['SemiC','SemiD'])[0:2], phase)

        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SemiA','SemiB'])[2:4], phase)
        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['SemiA','SemiB'])[0:2], phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.division.GetGroupsRanks(['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])

        self._GroupAddReferees('SemiA',[a_ranks[2]])
        self._GroupAddReferees('SemiB',[b_ranks[2]])

        # if self.teams_count > 11:
        #     self._GroupAddReferees('11th',[a_ranks[3]])
        # if self.teams_count > 9:
        #     self._GroupAddReferees('9th', [b_ranks[1]])
        # if self.teams_count > 7:
        #     self._GroupAddReferees('7th', [a_ranks[1]])
        # if self.teams_count > 5:
        #     self._GroupAddReferees('5th', [a_ranks[5]])

        self._GroupAddReferees('3rd',[self.division.GetGroupsRanks(['7th'])[0]])
        self._GroupAddReferees('final',[self.division.GetGroupsRanks(['5th'])[0]])
