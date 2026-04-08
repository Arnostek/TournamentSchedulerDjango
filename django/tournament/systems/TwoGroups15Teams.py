from .DivisionSystemBase import DivisionSystemBase

class TwoGroups15Teams(DivisionSystemBase):
    """ 2 zakladni skupiny, QF, SF, umisteni

    Nikdy nenasazeno - je potreba kontrola
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(TwoGroups15Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()

    def _createSystem(self):
        """
        BEFORE: 80 lines of repetitive code
        AFTER: 40 lines with clearer intent
        """

        # PHASE 1 - base groups
        self.phase.create_groups(['A', 'B'], self.division.seed_placeholders)
        ab_ranks = self.phase.get_ranks(['A', 'B'])

        # PHASE 2 - Quarter finals (first 8 teams)
        self.phase.next_phase()
        self.phase.create_groups(
            ['QF1', 'QF2', 'QF3', 'QF4'],
            ab_ranks[:8]
        )
        qf_ranks = self.phase.get_ranks(['QF1', 'QF2', 'QF3', 'QF4'])

        # PHASE 3 - Semi finals + secondary groups
        self.phase.next_phase()

        # Primary semis from QF winners
        self.phase.create_groups(['SF1', 'SF2'], qf_ranks[:4])

        # Secondary semis from QF losers
        self.phase.create_groups(['SF3', 'SF4'], qf_ranks[4:])

        # Additional group for teams 9-12
        self.phase.create_groups(['SF5', 'SF6'], ab_ranks[8:12])

        # Last 3 teams (13th place starts here)
        self.last3_builder.create_last3_group(['A', 'B'])

        # PHASE 4 - Placement matches using builder
        self.phase.next_phase()
        sf5_sf6_ranks = self.phase.get_ranks(['SF5', 'SF6'])
        sf3_sf4_ranks = self.phase.get_ranks(['SF3', 'SF4'])

        self.placements.create_placements_from_ranges({
            11: sf5_sf6_ranks[2:],
            9: sf5_sf6_ranks[:2],
            7: sf3_sf4_ranks[2:],
            5: sf3_sf4_ranks[:2],
        })

        # PHASE 5 - Finals
        self.phase.next_phase()
        sf1_sf2_ranks = self.phase.get_ranks(['SF1', 'SF2'])

        self.phase.create_and_rank('3rd', sf1_sf2_ranks[2:4], 3)
        self.phase.create_and_rank('Final', sf1_sf2_ranks[0:2], 1)
