from .DivisionSystemBase import DivisionSystemBase

class TwoGroups(DivisionSystemBase):
    """ Dve zakladni skupiny, semi pro 1. a 2., zapasy o misto """

    def __init__(self,tournament,division_name,division_slug,num_of_teams,last3=None,semi5_8=False):
        # zavolam konsturktor Predka
        super(TwoGroups, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True, semi5_8 = semi5_8, last3 = last3)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # PHASE 1 - zakladni skupiny
        self.phase.create_groups(['A','B'], self.division.seed_placeholders, referee_groups=['B','A'])
        ab_ranks = self.phase.get_ranks(['A','B'])

        self.phase.next_phase()
        # volitelne semi pro 5-8
        if self.semi5_8:
            self.phase.division.CreateGroups(['SemiC','SemiD'], ab_ranks[4:8], self.phase.phase)

        # prvni 4 tymy jdou do semi
        self.phase.division.CreateGroups(['SemiA','SemiB'], ab_ranks[:4], self.phase.phase)

        # pro lichy pocet tymu muze byt skupina poslednich tri
        if self.last3:
            # pro 9 zasahuje Last3 do semi C a D
            if self.semi5_8 and self.teams_count == 9:
                self.phase.division.CreateGroups(['Last3'],[self.division.GetGroupsRanks(['SemiC'])[-1], self.division.GetGroupsRanks(['SemiD'])[-1],  ab_ranks[-1]], self.phase.phase,['Last3'])
            else:
                self.phase.division.CreateGroups(['Last3'], ab_ranks[-3:], self.phase.phase,['Last3'])
            self.division.CreateRanks(self.teams_count - 2,self.division.GetGroupsRanks(['Last3']))

        # zapasy o mista
        self.phase.next_phase()
        if self.semi5_8:
            mista = [m for m in range(9,self.teams_count if not self.last3 else self.teams_count - 3,2)]
        else:
            mista = [m for m in range(5,self.teams_count if not self.last3 else self.teams_count - 3,2)]
        mista.reverse()
        for misto in mista:
            self.division.CreateGroups(['{}th'.format(misto)], ab_ranks[misto - 1: misto + 1], self.phase.phase)
            self.division.CreateRanks(misto,self.division.GetGroupsRanks(['{}th'.format(misto)]))

        if self.semi5_8:
            # pri deviti tymech a last # se o sedme misto nehraje
            if not(self.teams_count ==9 and self.last3):
                self.division.CreateGroups(['7th'], self.division.GetGroupsRanks(['SemiC','SemiD'])[2:4], self.phase.phase)
                self.division.CreateRanks(7,self.division.GetGroupsRanks(['7th']))

            self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['SemiC','SemiD'])[0:2], self.phase.phase)
            self.division.CreateRanks(5,self.division.GetGroupsRanks(['5th']))

        # 3rd
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', self.division.GetGroupsRanks(['SemiA','SemiB'])[2:4], 3)

        # Final
        self.phase.next_phase()
        self.phase.create_and_rank('Final', self.division.GetGroupsRanks(['SemiA','SemiB'])[0:2], 1)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.phase.get_ranks(['A'])
        b_ranks = self.phase.get_ranks(['B'])

        self.referees.assign_group_referees('SemiA',[a_ranks[2]])
        self.referees.assign_group_referees('SemiB',[b_ranks[2]])

        if self.semi5_8:
            self.referees.assign_group_referees('SemiC',[a_ranks[1]])
            self.referees.assign_group_referees('SemiD',[b_ranks[1]])

        if self.teams_count > 6 and self.semi5_8:
            self.referees.assign_group_referees('3rd',[self.division.GetGroupsRanks(['SemiA'])[0]])

        self.referees.assign_group_referees('Final',[self.division.GetGroupsRanks(['5th'])[0]])
