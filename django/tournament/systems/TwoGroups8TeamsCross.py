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
        self.phase.create_groups(['A','B'], self.division.seed_placeholders, referee_groups=['B','A'])

        # phase 2 - Krizove zapasy
        self.phase.next_phase()
        a_ranks = self.phase.get_ranks(['A'])
        b_ranks = self.phase.get_ranks(['B'])

        # zapasy 1. vs 4. a 2. vs 3.
        self.phase.create_groups(
            ['C1','C2','C3','C4'],
            [a_ranks[0],a_ranks[1],a_ranks[2],a_ranks[3],b_ranks[0],b_ranks[1],b_ranks[2],b_ranks[3]],
            referee_groups=['C3','C4','C1','C2']
        )

        # phase 3 - semi
        self.phase.next_phase()
        c_ranks = self.phase.get_ranks(['C1','C2','C3','C4'])

        # vitezove
        self.phase.create_groups(['S1','S2'], c_ranks[:4])

        # porazeni
        self.phase.create_groups(['S3','S4'], c_ranks[-4:], referee_groups=['S1','S2'])

        # umisteni
        # 7th, 5th
        self.phase.next_phase()
        s3_s4_ranks = self.phase.get_ranks(['S3','S4'])

        self.phase.division.CreateGroups(['7th'], s3_s4_ranks[2:4], self.phase.phase)
        self.phase.division.CreateRanks(7, self.phase.division.GetGroupsRanks(['7th']))

        self.phase.division.CreateGroups(['5th'], s3_s4_ranks[0:2], self.phase.phase)
        self.phase.division.CreateRanks(5, self.phase.division.GetGroupsRanks(['5th']))

        # 3rd
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', self.phase.get_ranks(['S1','S2'])[2:4], 3)

        # final
        self.phase.next_phase()
        self.phase.create_and_rank('final', self.phase.get_ranks(['S1','S2'])[0:2], 1)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        self.referees.assign_multiple_referees({
            'S1': self.division.GetGroupsRanks(['C3'])[-1:],
            'S2': self.division.GetGroupsRanks(['C2'])[-1:],
            '7th': self.division.GetGroupsRanks(['S1']),
            '5th': self.division.GetGroupsRanks(['S2']),
            '3rd': self.division.GetGroupsRanks(['7th']),
            'final': self.division.GetGroupsRanks(['5th']),
        })
