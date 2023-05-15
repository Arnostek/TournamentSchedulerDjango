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
        phase = 1
        # teams ref own group to be able shrink schedule
        self.division.CreateGroups(['A','B','C','D'], self.division.seed_placeholders, phase, referee_groups = ['C','D','A','B'])
        # phase 2 - two groups up, one down
        phase += 1
        phase1_ranks = self.division.GetGroupsRanks(['A','B','C','D'])
        self.division.CreateGroups(['E','F'], [phase1_ranks[0],phase1_ranks[4],phase1_ranks[1],phase1_ranks[5],phase1_ranks[2],phase1_ranks[6],phase1_ranks[3],phase1_ranks[7]], phase, referee_groups = ['F','E'])
        self.division.CreateGroups(['G'],phase1_ranks[8:], phase, referee_groups = ['G'])
        # first 4 teams go to semi
        phase += 1
        g_ranks = self.division.GetGroupsRanks(['G'])
        ef_ranks = self.division.GetGroupsRanks(['E','F'])
        self.division.CreateGroups(['SemiA','SemiB'], ef_ranks[:4], phase)
        # Finals
        phase += 1

        self.division.CreateGroups(['11th'],g_ranks[2:] , phase)
        self.division.CreateGroups(['9th'],g_ranks[:2] , phase)
        self.division.CreateGroups(['7th'],ef_ranks[6:8] , phase)
        self.division.CreateGroups(['5th'],ef_ranks[4:6] , phase)
        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SemiA','SemiB'])[2:4], phase)
        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['SemiA','SemiB'])[0:2], phase)

    def _addReferees(self):
        """ Referees for final matches """
        g_ranks = self.division.GetGroupsRanks(['G'])
        ef_ranks = self.division.GetGroupsRanks(['E','F'])
        self._GroupAddReferees('SemiA',[ef_ranks[4]])
        self._GroupAddReferees('SemiB',[ef_ranks[5]])
        self._GroupAddReferees('11th',[ef_ranks[7]])
        self._GroupAddReferees('9th',[ef_ranks[5]])
        self._GroupAddReferees('7th',[g_ranks[2]])
        self._GroupAddReferees('5th',[g_ranks[0]])
        self._GroupAddReferees('3rd',[ef_ranks[6]])
        self._GroupAddReferees('final',[ef_ranks[4]])
