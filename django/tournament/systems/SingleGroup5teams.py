from .DivisionSystemBase import DivisionSystemBase

class SingleGroup5teams(DivisionSystemBase):
    """ Jedna zakladni skupina, kazdy s kazdym, skupina tri poslednich kdo vypadne, semi a finale"""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(SingleGroup5teams, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - zakladni skupina
        phase = 1
        self.division.CreateGroups(['A'], self.division.seed_placeholders, phase, ['A'])
        a_ranks = self.division.GetGroupsRanks(['A'])
        # phase 2 - kdo opravdu vypadne
        phase += 1
        self.division.CreateGroups(['B'], [a_ranks[2], a_ranks[3], a_ranks[4]], phase, ['A'])
        b_ranks = self.division.GetGroupsRanks(['B'])

        # semi
        phase += 1
        self.division.CreateGroups(['SemiA'], [a_ranks[0], b_ranks[1]], phase)
        self.division.CreateGroups(['SemiB'], [a_ranks[1], b_ranks[0]], phase)

        # finals
        phase += 1
        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SemiA','SemiB'])[2:4] , phase)
        self.division.CreateGroups(['final'],self.division.GetGroupsRanks(['SemiA','SemiB'])[0:2] , phase)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        b_ranks = self.division.GetGroupsRanks(['B'])
        self._GroupAddReferees('SemiA', [b_ranks[0]])
        self._GroupAddReferees('SemiB', [b_ranks[1]])

        semi_ranks = self.division.GetGroupsRanks(['SemiA','SemiB'])
        self._GroupAddReferees('3rd', [semi_ranks[0]])
        self._GroupAddReferees('final', [semi_ranks[2]])
