from .DivisionSystemBase import DivisionSystemBase

class FourGroups13Teams(DivisionSystemBase):
    """ 4 zakladni skupiny, prvnich 8 jde nahoru ve dvou skupinach
    dolnich pet ma svou skupinu po ktere se konci. nahore jsou semi a zapasy o misto
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(FourGroups13Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()

    def _createSystem(self):
        # phase 1 - zakladni skupina
        self.phase.create_groups(
            ['A','B','C','D'],
            self.division.seed_placeholders,
            referee_groups=['C','D','A','B']
        )

        # dve horni a jedna dolni skupina
        self.phase.next_phase()
        phase1_ranks = self.phase.get_ranks(['A','B','C','D'])
        nasazeni_nahoru = phase1_ranks[:4]
        nasazeni_nahoru.extend([phase1_ranks[5],phase1_ranks[4],phase1_ranks[7],phase1_ranks[6]])
        self.phase.create_groups(['E','F'], nasazeni_nahoru, referee_groups=['F','E'])

        # group G uz konci
        self.phase.division.CreateGroups(['G'], phase1_ranks[8:], self.phase.phase)

        self.phase.next_phase()
        # prvni 4 tymy jdou do semi
        self.phase.create_groups(['SemiA','SemiB'], self.phase.get_ranks(['E','F'])[:4])

        # zapasy o mista bez semi
        self.phase.next_phase()
        mista = [m for m in [5,7]]
        mista.reverse()
        for misto in mista:
            self.division.CreateGroups(['{}th'.format(misto)], self.division.GetGroupsRanks(['E','F'])[misto - 1: misto + 1], self.phase.phase)
            self.division.CreateRanks(misto, self.division.GetGroupsRanks(['{}th'.format(misto)]))

        # 3rd
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', self.phase.get_ranks(['SemiA','SemiB'])[2:4], 3)

        # final
        self.phase.next_phase()
        self.phase.create_and_rank('final', self.phase.get_ranks(['SemiA','SemiB'])[0:2], 1)
