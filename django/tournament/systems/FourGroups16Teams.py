from .DivisionSystemBase import DivisionSystemBase

class FourGroups16Teams(DivisionSystemBase):
    """ 4 zakladni skupiny, QF, SF, umisteni
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(FourGroups16Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()

    def _createSystem(self):
        # phase 1 - zakladni skupina
        self.phase.create_groups(
            ['A','B','C','D'],
            self.division.seed_placeholders,
            referee_groups=['C','D','A','B']
        )
        abcd_ranks = self.phase.get_ranks(['A','B','C','D'])

        # QF - 1. vs 2., 3. vs 4.
        self.phase.next_phase()
        self.phase.create_groups(['QF1','QF2','QF3','QF4'], abcd_ranks[8:])
        self.phase.create_groups(['QF5','QF6','QF7','QF8'], abcd_ranks[:8])

        # SF
        self.phase.next_phase()
        qf1_4_ranks = self.phase.get_ranks(['QF1','QF2','QF3','QF4'])
        qf5_8_ranks = self.phase.get_ranks(['QF5','QF6','QF7','QF8'])

        self.phase.create_groups(['SF1','SF2'], qf1_4_ranks[:4])
        self.phase.create_groups(['SF3','SF4'], qf1_4_ranks[4:])
        self.phase.create_groups(['SF5','SF6'], qf5_8_ranks[:4])
        self.phase.create_groups(['SF7','SF8'], qf5_8_ranks[4:])

        # Places
        self.phase.next_phase()
        sf7_sf8_ranks = self.phase.get_ranks(['SF7','SF8'])
        sf5_sf6_ranks = self.phase.get_ranks(['SF5','SF6'])
        sf3_sf4_ranks = self.phase.get_ranks(['SF3','SF4'])

        self.placements.create_placements_from_ranges({
            15: sf7_sf8_ranks[2:],
            13: sf7_sf8_ranks[:2],
            11: sf5_sf6_ranks[2:],
            9: sf5_sf6_ranks[:2],
            7: sf3_sf4_ranks[2:],
            5: sf3_sf4_ranks[:2],
        })

        self.phase.create_and_rank('3rd', self.phase.get_ranks(['SF1','SF2'])[2:4], 3)

        # Final
        self.phase.next_phase()
        self.phase.create_and_rank('Final', self.phase.get_ranks(['SF1','SF2'])[:2], 1)
