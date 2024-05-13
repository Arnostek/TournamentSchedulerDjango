from .DivisionSystemBase import DivisionSystemBase

class SingleGroupDivisionSystem(DivisionSystemBase):
    """ Jedna zakladni skupina, kazdy s kazdym, zapas o 3. a prvni misto """

    def __init__(self,tournament,division_name,division_slug,num_of_teams,semi=False,final_for=None,last3=False):
        # zavolam konsturktor Predka
        super(SingleGroupDivisionSystem, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True,final_for = final_for,last3=last3)

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

        # semi
        if self.semi:
            phase += 1
            self.division.CreateGroups(['Semi1'], [a_ranks[1], a_ranks[2]] , phase)
            self.division.CreateGroups(['Semi2'],[a_ranks[0], a_ranks[3]] , phase)

        # last 3
        if self.last3:
            phase += 1
            self.division.CreateGroups(['Last3'], self.division.GetGroupsRanks(['A'])[-3:], phase,['Last3'])
            self.division.CreateRanks(num_of_teams - 2,d.GetGroupsRanks(['Last3']))

        # 5th
        if len(a_ranks) > 5 and self.final_for >= 5:
            phase += 1
            self.division.CreateGroups(['5th'], [a_ranks[4], a_ranks[5]] , phase)
            self.division.CreateRanks(5,self.division.GetGroupsRanks(['5th']))

        # final
        if self.semi:

            semi_ranks = self.division.GetGroupsRanks(['Semi1','Semi2'])
            # 3rd
            phase += 1
            self.division.CreateGroups(['3rd'], [semi_ranks[2], semi_ranks[3]] , phase)
            # final
            phase += 1
            self.division.CreateGroups(['final'],[semi_ranks[0], semi_ranks[1]] , phase)

        else:
            # 3rd
            if len(a_ranks) > 3 and self.final_for >= 3:
                phase += 1
                self.division.CreateGroups(['3rd'], [a_ranks[2], a_ranks[3]] , phase)
            # final
            phase += 1
            self.division.CreateGroups(['final'],[a_ranks[0], a_ranks[1]] , phase)

        self.division.CreateRanks(3,self.division.GetGroupsRanks(['3rd']))
        self.division.CreateRanks(1,self.division.GetGroupsRanks(['final']))


    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        a_ranks = self.division.GetGroupsRanks(['A'])
        if len(a_ranks) > 5 and self.final_for >= 3:
            self._GroupAddReferees('3rd',[a_ranks[5]])
        if len(a_ranks) > 4:
            self._GroupAddReferees('final',[a_ranks[4]])
