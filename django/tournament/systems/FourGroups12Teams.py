from .DivisionSystemBase import DivisionSystemBase

class FourGroups12Teams(DivisionSystemBase):
    """ phase 1 - 4 basic groups,
        phase 2 - first 8 teams go to 2 groups up rest go down
        semi
        finals
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(FourGroups12Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # add referees
        self._addReferees()

    def _createSystem(self):
        # phase 1 - basic groups
        self.phase.create_groups(
            ['A','B','C','D'],
            self.division.seed_placeholders,
            referee_groups=['C','D','A','B']
        )

        # phase 2 - two groups up, one down
        self.phase.next_phase()
        phase1_ranks = self.phase.get_ranks(['A','B','C','D'])
        self.phase.create_groups(
            ['E','F'],
            [phase1_ranks[0],phase1_ranks[4],phase1_ranks[1],phase1_ranks[5],phase1_ranks[2],phase1_ranks[6],phase1_ranks[3],phase1_ranks[7]],
            referee_groups=['F','E']
        )
        self.phase.create_groups(['G'], phase1_ranks[8:], referee_groups=['G'])

        # first 4 teams go to semi
        self.phase.next_phase()
        g_ranks = self.phase.get_ranks(['G'])
        ef_ranks = self.phase.get_ranks(['E','F'])
        self.phase.create_groups(['SemiA','SemiB'], ef_ranks[:4])

        # Finals
        self.phase.next_phase()

        self.phase.division.CreateGroups(['11th'], g_ranks[2:], self.phase.phase)
        self.phase.division.CreateRanks(11, self.phase.division.GetGroupsRanks(['11th']))

        self.phase.division.CreateGroups(['9th'], g_ranks[:2], self.phase.phase)
        self.phase.division.CreateRanks(9, self.phase.division.GetGroupsRanks(['9th']))

        self.phase.division.CreateGroups(['7th'], ef_ranks[6:8], self.phase.phase)
        self.phase.division.CreateRanks(7, self.phase.division.GetGroupsRanks(['7th']))

        self.phase.division.CreateGroups(['5th'], ef_ranks[4:6], self.phase.phase)
        self.phase.division.CreateRanks(5, self.phase.division.GetGroupsRanks(['5th']))

        # 3rd
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', self.phase.get_ranks(['SemiA','SemiB'])[2:4], 3)

        # final
        self.phase.next_phase()
        self.phase.create_and_rank('final', self.phase.get_ranks(['SemiA','SemiB'])[0:2], 1)

    def _addReferees(self):
        """ Referees for final matches """
        g_ranks = self.phase.get_ranks(['G'])
        ef_ranks = self.phase.get_ranks(['E','F'])

        self.referees.assign_multiple_referees({
            'SemiA': [ef_ranks[4]],
            'SemiB': [ef_ranks[5]],
            '11th': [ef_ranks[7]],
            '9th': [ef_ranks[5]],
            '7th': [g_ranks[2]],
            '5th': [g_ranks[0]],
            '3rd': [ef_ranks[6]],
            'final': [ef_ranks[4]],
        })
