from .DivisionSystemBase import DivisionSystemBase

class TwoGroups8Teams(DivisionSystemBase):
    """ Two groups, Lower and Higher group, finals"""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(TwoGroups8Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = False)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        """System definition using builders - much cleaner!"""

        # PHASE 1 - first round
        self.phase.create_groups(
            ['A', 'B'],
            self.division.seed_placeholders,
            referee_groups=['B', 'A']
        )

        # PHASE 2 - second round
        self.phase.next_phase()
        a_ranks = self.phase.get_ranks(['A'])
        b_ranks = self.phase.get_ranks(['B'])

        # Mix teams from A and B
        mixed_seeds = [
            a_ranks[0], a_ranks[2], b_ranks[2], b_ranks[0],
            a_ranks[1], a_ranks[3], b_ranks[3], b_ranks[1]
        ]
        self.phase.create_groups(['C', 'D'], mixed_seeds, referee_groups=['D', 'C'])

        # PHASE 3 - placement matches
        self.phase.next_phase()
        c_ranks = self.phase.get_ranks(['C'])
        d_ranks = self.phase.get_ranks(['D'])

        # Use PlacementBuilder for 7th and 5th place matches
        self.placements.create_placements_from_ranges({
            7: d_ranks[2:4],
            5: d_ranks[0:2],
        })

        # PHASE 4 - Finals
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', c_ranks[2:4], 3)
        self.phase.create_and_rank('Final', c_ranks[0:2], 1)

    def _addReferees(self):
        """Simplified referee assignment using RefereeBuilder."""
        a_ranks = self.phase.get_ranks(['A'])
        b_ranks = self.phase.get_ranks(['B'])
        c_ranks = self.phase.get_ranks(['C'])
        d_ranks = self.phase.get_ranks(['D'])

        self.referees.assign_multiple_referees({
            '7th': [d_ranks[1]],
            '5th': [d_ranks[2]],
            '3rd': [d_ranks[0]],
            'Final': [c_ranks[2]],
        })
