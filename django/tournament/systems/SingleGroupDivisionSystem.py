from .DivisionSystemBase import DivisionSystemBase

class SingleGroupDivisionSystem(DivisionSystemBase):
    """ Jedna zakladni skupina, kazdy s kazdym, zapas o 3. a prvni misto """

    def __init__(self,tournament,division_name,division_slug,teams_count,semi=False,final_for=None,last3=False):
        # zavolam konsturktor Predka
        super(SingleGroupDivisionSystem, self).__init__(tournament,division_name,division_slug,teams_count,semi = semi,final_for = final_for,last3=last3)

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

        phase += 1
        # semi
        if self.semi:
            self.division.CreateGroups(['Semi1'], [a_ranks[1], a_ranks[2]] , phase)
            self.division.CreateGroups(['Semi2'],[a_ranks[0], a_ranks[3]] , phase)

        # last 3
        if self.last3:
            self.division.CreateGroups(['Last3'], self.division.GetGroupsRanks(['A'])[-3:], phase,['Last3'])
            self.division.CreateRanks(self.teams_count - 2,self.division.GetGroupsRanks(['Last3']))

        # 5th
        if len(a_ranks) > 5 and self.final_for >= 5:
            self.division.CreateGroups(['5th'], [a_ranks[4], a_ranks[5]] , phase)
            self.division.CreateRanks(5,self.division.GetGroupsRanks(['5th']))

        # final
        if self.semi:
            semi_ranks = self.division.GetGroupsRanks(['Semi1','Semi2'])
            # 3rd
            self.division.CreateGroups(['3rd'], [semi_ranks[2], semi_ranks[3]] , phase)
            self.division.CreateRanks(3,self.division.GetGroupsRanks(['3rd']))
            # final
            self.division.CreateGroups(['Final'],[semi_ranks[0], semi_ranks[1]] , phase)
            self.division.CreateRanks(1,self.division.GetGroupsRanks(['Final']))

        else:
            # 3rd
            if len(a_ranks) > 3 and self.final_for >= 3:
                self.division.CreateGroups(['3rd'], [a_ranks[2], a_ranks[3]] , phase)
                self.division.CreateRanks(3,self.division.GetGroupsRanks(['3rd']))
            # final
            self.division.CreateGroups(['Final'],[a_ranks[0], a_ranks[1]] , phase)
            self.division.CreateRanks(1,self.division.GetGroupsRanks(['Final']))

        # nakonec potebujeme dodelat ranking pro vsechny co nikam nepostupuji
        first_direct_rank_index = 2

        # semifinale nebo zapas o 3. misto znamena, ze tymy 1-4 pokracuji
        if self.semi or (len(a_ranks) > 3 and self.final_for >= 3):
            first_direct_rank_index = 4

        # zapas o 5. misto znamena, ze tymy 5-6 pokracuji
        if len(a_ranks) > 5 and self.final_for >= 5:
            first_direct_rank_index = 6

        # pokud se hraje Last3, posledni tri tymy maji jeste zapasy
        direct_ranks_end_index = len(a_ranks) - 3 if self.last3 else len(a_ranks)

        if first_direct_rank_index < direct_ranks_end_index:
            self.division.CreateRanks(
                first_direct_rank_index + 1,
                a_ranks[first_direct_rank_index:direct_ranks_end_index]
            )


    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.division.GetGroupsRanks(['A'])
        if len(a_ranks) > 5 and self.final_for >= 3:
            self._GroupAddReferees('3rd',[a_ranks[5]])
        if len(a_ranks) > 4:
            self._GroupAddReferees('Final',[a_ranks[4]])
