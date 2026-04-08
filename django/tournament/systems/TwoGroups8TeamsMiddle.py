from .DivisionSystemBase import DivisionSystemBase

class TwoGroups8TeamsMiddle(DivisionSystemBase):
    """ Two groups, Cross matches 2nd against 3rd, Lower and Higher group, finals for top 4"""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(TwoGroups8TeamsMiddle, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = False)
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

        # zapasy 2. vs 3.
        self.phase.create_groups(['M1','M2'], [a_ranks[1],a_ranks[2],b_ranks[1],b_ranks[2]])

        # phase 3 - druhe kolo
        self.phase.next_phase()
        m_ranks = self.phase.get_ranks(['M1','M2'])

        # vitezove
        self.phase.create_groups(['C'], self.phase.get_ranks(['A','B','M1','M2'])[:4], referee_groups=['C'])

        # porazeni
        self.phase.create_groups(['D'], m_ranks[-2:] + self.phase.get_ranks(['A','B'])[-2:], referee_groups=['D'])

        # umisteni
        # 3rd
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', self.phase.get_ranks(['C'])[2:4], 3)

        # final
        self.phase.next_phase()
        self.phase.create_and_rank('final', self.phase.get_ranks(['C'])[0:2], 1)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        self.referees.assign_multiple_referees({
            'M1': self.phase.get_ranks(['A']),
            'M2': self.phase.get_ranks(['B']),
        })
