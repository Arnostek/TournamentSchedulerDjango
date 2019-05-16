from .DivisionSystemBase import DivisionSystemBase

class FourGroups13Teams(DivisionSystemBase):
    """ 4 zakladni skupiny, prvnich 8 jde nahoru ve dvou skupinach
    dolnich pet ma svou skupinu po ktere se konci. nahore jsou semi a zapasy o misto
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(FourGroups13Teams, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()

    def _createSystem(self):
        # phase 1 - zakladni skupina
        phase = 1
        self.division.CreateGroups(['A','B','C','D'], self.division.seed_placeholders, phase)
        # dve horni a jedna dolni skupina
        phase += 1
        phase1_ranks = self.division.GetGroupsRanks(['A','B','C','D'])
        nasazeni_nahoru = phase1_ranks[:4]
        nasazeni_nahoru.extend([phase1_ranks[5],phase1_ranks[4],phase1_ranks[7],phase1_ranks[6]])
        self.division.CreateGroups(['E','F'],nasazeni_nahoru , phase)
        self.division.CreateGroups(['G'], self.division.GetGroupsRanks(['A','B','C','D'])[8:], phase)
        # prvni 4 tymy jdou do semi
        phase += 1
        self.division.CreateGroups(['SemiA','SemiB'], self.division.GetGroupsRanks(['E','F'])[:4], phase)
        # zapasy o mista bez semi
        phase += 1
        mista = [m for m in [5,7]]
        mista.reverse()
        for misto in mista:
            self.division.CreateGroups(['{}th'.format(misto)], self.division.GetGroupsRanks(['E','F'])[misto - 1: misto + 1], phase)
        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SemiA','SemiB'])[2:4], phase)
        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['SemiA','SemiB'])[0:2], phase)
