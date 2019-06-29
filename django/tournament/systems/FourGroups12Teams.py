from .DivisionSystemBase import DivisionSystemBase

class FourGroups12Teams(DivisionSystemBase):
    """ phase 1 - 4 basic groups,
        phase 2 - first 8 teams go to 2 groups up rest go down
        semi
        finals
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(FourGroups12Teams, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()

    def _createSystem(self):
        # phase 1 - basic groups
        phase = 1
        self.division.CreateGroups(['A','B','C','D'], self.division.seed_placeholders, phase)
        # phase 2 - two groups up, one down
        phase += 1
        phase1_ranks = self.division.GetGroupsRanks(['A','B','C','D'])
        a_ranks = self.division.GetGroupsRanks(['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])
        c_ranks = self.division.GetGroupsRanks(['C'])
        d_ranks = self.division.GetGroupsRanks(['D'])
        self.division.CreateGroups(['X'],[a_ranks[0] , b_ranks[0] , c_ranks[1] , d_ranks[1] ], phase)
        self.division.CreateGroups(['Y'],[a_ranks[1] , b_ranks[1] , c_ranks[0] , d_ranks[0] ], phase)
        self.division.CreateGroups(['Z'],[a_ranks[2] , b_ranks[2] , c_ranks[2] , d_ranks[2] ], phase)
        # first 4 teams go to semi
        phase += 1
        z_ranks = self.division.GetGroupsRanks(['Z'])
        xy_ranks = self.division.GetGroupsRanks(['X','Y'])
        self.division.CreateGroups(['SemiA','SemiB'], xy_ranks[:4], phase)
        # Finals
        phase += 1

        self.division.CreateGroups(['11th'],z_ranks[:2] , phase)
        self.division.CreateGroups(['9th'],z_ranks[2:] , phase)
        self.division.CreateGroups(['7th'],xy_ranks[7:8] , phase)
        self.division.CreateGroups(['5th'],xy_ranks[5:6] , phase)
        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SemiA','SemiB'])[2:4], phase)
        # final
        phase += 1
        self.division.CreateGroups(['final'], self.division.GetGroupsRanks(['SemiA','SemiB'])[0:2], phase)
