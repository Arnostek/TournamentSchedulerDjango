from .DivisionSystemBase import DivisionSystemBase

class SingleGroupDivisionSystem(DivisionSystemBase):
    """ Jedna zakladni skupina, kazdy s kazdym, zapas o 3. a prvni misto """

    def __init__(self,tournament,division_name,division_slug,num_of_teams,semi=False,final_for=None,last3=False):
        # zavolam konsturktor Predka
        super(SingleGroupDivisionSystem, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = semi,final_for = final_for,last3=last3)

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

        # semi
        if self.semi:
            self.phase.next_phase()
            self.phase.division.CreateGroups(['Semi1'], [a_ranks[1], a_ranks[2]], self.phase.phase)
            self.phase.division.CreateGroups(['Semi2'], [a_ranks[0], a_ranks[3]], self.phase.phase)

        # last 3
        if self.last3:
            self.phase.next_phase()
            self.phase.division.CreateGroups(['Last3'], a_ranks[-3:], self.phase.phase, ['Last3'])
            self.division.CreateRanks(self.teams_count - 2, self.division.GetGroupsRanks(['Last3']))

        # 5th
        if len(a_ranks) > 5 and self.final_for >= 5:
            self.phase.next_phase()
            self.phase.division.CreateGroups(['5th'], [a_ranks[4], a_ranks[5]], self.phase.phase)
            self.division.CreateRanks(5, self.division.GetGroupsRanks(['5th']))

        # final
        if self.semi:
            semi_ranks = self.division.GetGroupsRanks(['Semi1','Semi2'])
            # 3rd
            self.phase.next_phase()
            self.phase.create_and_rank('3rd', [semi_ranks[2], semi_ranks[3]], 3)
            # final
            self.phase.next_phase()
            self.phase.create_and_rank('final', [semi_ranks[0], semi_ranks[1]], 1)

        else:
            # 3rd
            if len(a_ranks) > 3 and self.final_for >= 3:
                self.phase.next_phase()
                self.phase.create_and_rank('3rd', [a_ranks[2], a_ranks[3]], 3)
            # final
            self.phase.next_phase()
            self.phase.create_and_rank('final', [a_ranks[0], a_ranks[1]], 1)


    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.phase.get_ranks(['A'])
        if len(a_ranks) > 5 and self.final_for >= 3:
            self.referees.assign_group_referees('3rd', [a_ranks[5]])
        if len(a_ranks) > 4:
            self.referees.assign_group_referees('final', [a_ranks[4]])
