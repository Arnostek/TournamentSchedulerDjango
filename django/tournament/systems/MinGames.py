from .DivisionSystemBase import DivisionSystemBase

class MinGames16Teams(DivisionSystemBase):
    """ 4 zakladni skupiny, pak rozdeleno na horni a dolni kde kazdy odehraje prave jeden zapas. Pricitaji se body z minule. Semi a zapasy o misto."""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(MinGames16Teams, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()

    def _createSystem(self):
        # phase 1 - zakladni skupiny
        phase = 1
        self.division.CreateGroups(['A','B','C','D'], self.division.seed_placeholders, phase)
        # dolni a horni skupina, kde kazdy hraje jednou, zapasy vygenerujeme rucne
        phase += 1
        self.division.CreateGroups(['E'], self.division.GetGroupsRanks(['A','B','C','D'])[:8], phase)
        e_group = self.division.group_set.last()
        e_group.CreateMatch((1,8,3))
        e_group.CreateMatch((2,7,3))
        e_group.CreateMatch((3,6,3))
        e_group.CreateMatch((4,5,3))

        self.division.CreateGroups(['F'], self.division.GetGroupsRanks(['A','B','C','D'])[8:], phase)
        f_group = self.division.group_set.last()
        f_group.CreateMatch((1,8,3))
        f_group.CreateMatch((2,7,3))
        f_group.CreateMatch((3,6,3))
        f_group.CreateMatch((4,5,3))
        # semi
        phase += 1
        self.division.CreateGroups(['SemiA','SemiB'], self.division.GetGroupsRanks(['E','F'])[:4], phase)
        # zapasy o mista bez semi
        phase += 1
        for misto in [15,13,11,9,7,5]:
            self.division.CreateGroups(['{}th'.format(misto)], self.division.GetGroupsRanks(['E','F'])[misto - 1: misto + 1], phase)
        # 3rd
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SemiA','SemiB'])[2:4], 5)
        # final
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['SemiA','SemiB'])[0:2], 6)


class MinGames6Teams(DivisionSystemBase):
    """ 2 zakladni skupiny, pak jedna velka skupina kde kazdy odehraje dva zapasy. Pricitaji se body z minule. Nasleduji zapasy o misto."""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(MinGames6Teams, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()

    def _createSystem(self):
        self.division.CreateGroups(['A','B'], self.division.seed_placeholders, 1)
        # skupina, kde se neodehraje vsechno, zapasy vygenerujeme rucne
        self.division.CreateGroups(['C'], self.division.GetGroupsRanks(['A','B']), 2)
        c_group = self.division.group_set.last()
        c_group.CreateMatch((1,4,0))
        c_group.CreateMatch((3,6,0))
        c_group.CreateMatch((5,2,0))
        c_group.CreateMatch((1,6,1))
        c_group.CreateMatch((3,2,1))
        c_group.CreateMatch((5,4,1))
        #5th
        self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['C'])[4:6], 3)
        # 3rd
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['C'])[2:4], 4)
        # final
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['C'])[0:2], 5)
        # vygenerovani zapasu
        self.division.CreateMatches()
