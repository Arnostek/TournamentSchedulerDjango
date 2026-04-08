from .DivisionSystemBase import DivisionSystemBase

class ThreeGroups15Teams(DivisionSystemBase):
    """ 3 zakladni skupiny, meziskupiny, QF, SF, umisteni
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(ThreeGroups15Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):

        # PHASE 1 - Three base groups
        self.phase.create_groups(
            ['A', 'B', 'C'],
            self.division.seed_placeholders,
            referee_groups=['A', 'B', 'C']
        )

        # PHASE 2 - Inter-group matches (complex seeding with PlacementBuilder)
        self.phase.next_phase()
        a_ranks = self.phase.get_ranks(['A'])
        b_ranks = self.phase.get_ranks(['B'])
        c_ranks = self.phase.get_ranks(['C'])

        # Top 6 teams
        self.phase.create_groups(['E'], [a_ranks[0], b_ranks[1], c_ranks[0]], referee_groups=['E'])
        self.phase.create_groups(['F'], [a_ranks[1], b_ranks[0], c_ranks[1]], referee_groups=['F'])

        # Places 7-12
        self.phase.create_groups(['G'], [a_ranks[2], b_ranks[3], c_ranks[2]], referee_groups=['G'])
        self.phase.create_groups(['H'], [a_ranks[3], b_ranks[2], c_ranks[3]], referee_groups=['H'])

        # PHASE 3 - Semis from top-ranked groups
        self.phase.next_phase()
        ef_ranks = self.phase.get_ranks(['E', 'F'])
        self.phase.create_groups(['SF1', 'SF2'], ef_ranks[:4])

        # PHASE 4 - Placements using builder
        self.phase.next_phase()
        gh_ranks = self.phase.get_ranks(['G', 'H'])

        self.placements.create_placements_from_ranges({
            11: gh_ranks[4:6],
            9: gh_ranks[2:4],
            7: gh_ranks[:2],
            5: ef_ranks[4:],
        })

        # PHASE 5 - Last3 and Finals
        self.phase.next_phase()
        abc_ranks = self.phase.get_ranks(['A', 'B', 'C'])
        self.last3_builder.create_last3_group(['A', 'B', 'C'])

        sf_ranks = self.phase.get_ranks(['SF1', 'SF2'])
        self.phase.create_and_rank('3rd', sf_ranks[2:4], 3)
        self.phase.create_and_rank('Final', sf_ranks[0:2], 1)

    def _addReferees(self):
        """Clean referee assignment using builder."""
        gh_ranks = self.phase.get_ranks(['G', 'H'])
        ef_ranks = self.phase.get_ranks(['E', 'F'])

        self.referees.assign_multiple_referees({
            'SF1': [ef_ranks[4]],
            'SF2': [ef_ranks[5]],
            '11th': [ef_ranks[3]],
            '9th': [ef_ranks[2]],
            '7th': [gh_ranks[2]],
            '5th': [gh_ranks[0]],
            '3rd': [ef_ranks[5]],
            'Final': [ef_ranks[4]],
        })
