from .DivisionSystemBase import DivisionSystemBase

class SingleGroup5teams(DivisionSystemBase):
    """ Jedna zakladni skupina, kazdy s kazdym, skupina tri poslednich kdo vypadne, semi a finale"""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(SingleGroup5teams, self).__init__(tournament,division_name,division_slug,num_of_teams, semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - zakladni skupina
        self.phase.create_groups(['A'], self.division.seed_placeholders, referee_groups=['A'])
        a_ranks = self.phase.get_ranks(['A'])

        # phase 2 - kdo opravdu vypadne
        self.phase.next_phase()
        self.phase.create_groups(['B'], [a_ranks[2], a_ranks[3], a_ranks[4]])
        b_ranks = self.phase.get_ranks(['B'])

        # semi
        self.phase.next_phase()
        self.phase.create_groups(['SemiA'], [a_ranks[0], b_ranks[1]])
        self.phase.create_groups(['SemiB'], [a_ranks[1], b_ranks[0]])

        # finals
        self.phase.next_phase()
        semi_ranks = self.phase.get_ranks(['SemiA','SemiB'])
        self.phase.create_and_rank('3rd', semi_ranks[2:4], 3)
        self.phase.create_and_rank('final', semi_ranks[0:2], 1)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        b_ranks = self.phase.get_ranks(['B'])
        semi_ranks = self.phase.get_ranks(['SemiA','SemiB'])

        self.referees.assign_multiple_referees({
            'SemiA': [b_ranks[0]],
            'SemiB': [b_ranks[1]],
            '3rd': [semi_ranks[0]],
            'final': [semi_ranks[2]],
        })
