from .DivisionSystemBase import DivisionSystemBase

class SingleGroupDivisionSystem(DivisionSystemBase):
    """ Jedna zakladni skupina, kazdy s kazdym, zapas o 3. a prvni misto """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(SingleGroupDivisionSystem, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()

    def _createSystem(self):
        # phase 1 - zakladni skupina
        phase = 1
        self.division.CreateGroups(['A'], self.division.seed_placeholders, phase, ['A'])
        a_ranks = self.division.GetGroupsRanks(['A'])
        # 3rd
        phase += 1
        self.division.CreateGroups(['3rd'], [a_ranks[2], a_ranks[3]] , phase)
        if len(a_ranks) > 5:
            self._lastMatchAddReferee(a_ranks[5])
        # final
        phase += 1
        self.division.CreateGroups(['final'],[a_ranks[0], a_ranks[1]] , phase)
        if len(a_ranks) > 4:
            self._lastMatchAddReferee(a_ranks[4])
