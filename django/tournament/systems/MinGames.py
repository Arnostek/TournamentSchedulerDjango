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
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - zakladni skupiny
        phase = 1
        self.division.CreateGroups(['A','B','C','D'], self.division.seed_placeholders, phase, ['B','C','D','A'])
        # dolni a horni skupina, kde kazdy hraje jednou, zapasy vygenerujeme rucne
        phase += 1
        self.division.CreateGroups(['E'], self.division.GetGroupsRanks(['A','B','C','D'])[:8], phase)
        e_group = self.division.group_set.last()
        self.division.CreateGroups(['F'], self.division.GetGroupsRanks(['A','B','C','D'])[8:], phase)
        f_group = self.division.group_set.last()

        # zapasy skupin E a F
        e_group.CreateMatch((1,8,3))
        e_group.CreateMatch((2,7,3))
        f_group.CreateMatch((1,8,3))
        f_group.CreateMatch((2,7,3))
        e_group.CreateMatch((3,6,3))
        e_group.CreateMatch((4,5,3))
        f_group.CreateMatch((3,6,3))
        f_group.CreateMatch((4,5,3))
        # semi - prvni 4 tymy z horni skupiny
        phase += 1
        self.division.CreateGroups(['SemiA','SemiB'], self.division.GetGroupsRanks(['E'])[:4], phase)
        # zapasy o mista bez semi
        phase += 1
        for misto in [15,13,11,9]:
            self.division.CreateGroups(['{}th'.format(misto)], self.division.GetGroupsRanks(['F'])[misto - 9: misto -7], phase)
        for misto in [7,5]:
            self.division.CreateGroups(['{}th'.format(misto)], self.division.GetGroupsRanks(['E'])[misto - 1: misto + 1], phase)
        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SemiA','SemiB'])[2:4], phase)
        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['SemiA','SemiB'])[0:2], phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        # gropy E a F
        phase1_ranks = self.division.GetGroupsRanks(['A','B','C','D'])
        self._GroupAddReferees('E',[phase1_ranks[0],phase1_ranks[1],phase1_ranks[2],phase1_ranks[3]])
        self._GroupAddReferees('F',[phase1_ranks[8],phase1_ranks[9],phase1_ranks[10],phase1_ranks[11]])
        # Semi
        groupE_ranks = self.division.GetGroupsRanks(['E'])
        groupF_ranks = self.division.GetGroupsRanks(['F'])
        self._GroupAddReferees('SemiA',[groupE_ranks[4]])
        self._GroupAddReferees('SemiB',[groupE_ranks[5]])
        # umisteni
        self._GroupAddReferees('15th',[groupF_ranks[0]])
        self._GroupAddReferees('13th',[groupF_ranks[1]])
        self._GroupAddReferees('11th',[groupF_ranks[7]])
        self._GroupAddReferees('9th',[groupF_ranks[6]])
        self._GroupAddReferees('7th',[groupF_ranks[4]])
        self._GroupAddReferees('5th',[self.division.GetGroupsRanks(['11th'])[0]])
        self._GroupAddReferees('3rd',[self.division.GetGroupsRanks(['9th'])[0]])
        self._GroupAddReferees('final',[self.division.GetGroupsRanks(['7th'])[0]])


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
        phase = 1
        self.division.CreateGroups(['A','B'], self.division.seed_placeholders, phase)
        # skupina, kde se neodehraje vsechno, zapasy vygenerujeme rucne
        phase += 1
        self.division.CreateGroups(['C'], self.division.GetGroupsRanks(['A','B']), phase)
        c_group = self.division.group_set.last()
        c_group.CreateMatch((1,4,0))
        c_group.CreateMatch((3,6,0))
        c_group.CreateMatch((5,2,0))
        c_group.CreateMatch((1,6,1))
        c_group.CreateMatch((3,2,1))
        c_group.CreateMatch((5,4,1))
        #5th
        phase += 1
        self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['C'])[4:6], phase)
        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['C'])[2:4], phase)
        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['C'])[0:2], phase)
        # vygenerovani zapasu
        self.division.CreateMatches()
