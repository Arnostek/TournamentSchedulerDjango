from .DivisionSystemBase import DivisionSystemBase

class FourGroups15Teams(DivisionSystemBase):
    """ 4 zakladni skupiny, QF, SF, umisteni
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(FourGroups15Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - zakladni skupina. Skupiny 4,4,4 a 3
        self.phase.create_groups(
            ['A','B','C','D'],
            self.division.seed_placeholders,
            referee_groups=['C','D','A','B']
        )
        abcd_ranks = self.phase.get_ranks(['A','B','C','D'])

        # QF - 1. vs 2., 3. vs 4. + X3
        self.phase.next_phase()
        # QF ze tretich mist
        self.phase.create_groups(['EF1','EF2'], abcd_ranks[8:12], referee_groups=['EF1','EF2'])

        # skupina 4. mist
        self.phase.create_groups(['E'], abcd_ranks[12:], referee_groups=['E'])

        # QF z prvnich a druhych mist
        self.phase.create_groups(
            ['QF1','QF2','QF3','QF4'],
            abcd_ranks[:8],
            referee_groups=['QF1','QF2','QF3','QF4']
        )

        # SF + spodek
        self.phase.next_phase()
        ef_ranks = self.phase.get_ranks(['EF1','EF2','E'])

        # skupina porazeni dolniho QF a 1. E
        self.phase.create_groups(['F'], ef_ranks[2:5], referee_groups=['F'])

        # vitezove dolniho QF
        self.phase.create_groups(['M1'], self.phase.get_ranks(['EF1','EF2'])[:2])

        # vitezove horniho QF
        qf_ranks = self.phase.get_ranks(['QF1','QF2','QF3','QF4'])
        self.phase.create_groups(['SF1','SF2'], qf_ranks[:4])

        # porazeni horniho QF
        self.phase.create_groups(['SF3','SF4'], qf_ranks[4:])

        # spodek
        self.phase.create_groups(['SF5','SF6'], self.phase.get_ranks(['M1','F'])[:4])

        # Places
        self.phase.next_phase()
        # skupina posledni 3
        self.last3_builder.create_last3_group(['E','F'])

        # zapasy o mista
        sf5_sf6_ranks = self.phase.get_ranks(['SF5','SF6'])
        sf3_sf4_ranks = self.phase.get_ranks(['SF3','SF4'])

        self.placements.create_placements_from_ranges({
            11: sf5_sf6_ranks[2:],
            9: sf5_sf6_ranks[:2],
            7: sf3_sf4_ranks[2:],
            5: sf3_sf4_ranks[:2],
        })

        self.phase.create_and_rank('3rd', self.phase.get_ranks(['SF1','SF2'])[2:4], 3)

        # Final
        self.phase.next_phase()
        self.phase.create_and_rank('Final', self.phase.get_ranks(['SF1','SF2'])[:2], 1)
        
    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        abcd_ranks = self.phase.get_ranks(['A', 'B', 'C', 'D'])
        qf_ranks = self.phase.get_ranks(['QF1', 'QF2','QF3', 'QF4'])

        self.referees.assign_multiple_referees({
            'EF1': [abcd_ranks[4]],
            'EF2': [abcd_ranks[5]],
            'M1': [self.phase.get_ranks(['EF1', 'B'])[1]],
            'QF1': [abcd_ranks[8]],
            'QF2': [abcd_ranks[9]],
            'QF3': [abcd_ranks[10]],
            'QF4': [abcd_ranks[11]],
            'SF1': [qf_ranks[4]],
            'SF2': [qf_ranks[5]],
            'SF3': [qf_ranks[0]],
            'SF4': [qf_ranks[1]],
            'SF5': [qf_ranks[2]],
            'SF6': [qf_ranks[3]],
            '7th': [self.division.GetGroupsRanks(['11th'])[0]],
            '5th': [self.division.GetGroupsRanks(['9th'])[0]],
            '3rd': [self.division.GetGroupsRanks(['7th'])[0]],
            'Final': [self.division.GetGroupsRanks(['5th'])[0]],
        })
