from .DivisionSystemBase import DivisionSystemBase

class ThreeGroups9Teams(DivisionSystemBase):
    """ 3 zakladni skupiny, meziskupiny, QF, SF, umisteni
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(ThreeGroups9Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - zakladni skupina. Skupiny 3,3,3
        phase = 1
        self.division.CreateGroups(['A','B','C'], self.division.seed_placeholders, phase, ['A','B','C'])

        # meziskupiny
        phase += 1
        self.division.CreateGroups(['E'], self.division.GetGroupsRanks(['A','B','C'])[0:3], phase, ['E'])
        self.division.CreateGroups(['F'], self.division.GetGroupsRanks(['A','B','C'])[3:6], phase, ['F'])
        self.division.CreateGroups(['G1'], self.division.GetGroupsRanks(['A','B','C'])[6:], phase, ['G1'])

        # # SF pro 1-4
        phase += 1
        self.division.CreateGroups(['SF1'], [self.division.GetGroupsRanks(['E'])[0], self.division.GetGroupsRanks(['F'])[0]], phase)
        self.division.CreateGroups(['SF2'], [self.division.GetGroupsRanks(['E'])[1], self.division.GetGroupsRanks(['E'])[2]], phase)
        self.division.CreateGroups(['H1'], [self.division.GetGroupsRanks(['F'])[1], self.division.GetGroupsRanks(['F'])[2]], phase)

        # places
        phase += 1
        self.division.CreateGroups(['G2'], self.division.GetGroupsRanks(['A','B','C'])[6:], phase, ['G2'])
        self.division.CreateRanks(7,self.division.GetGroupsRanks(['G2']))

        self.division.CreateGroups(['H2'], [self.division.GetGroupsRanks(['F'])[1], self.division.GetGroupsRanks(['F'])[2]], phase, ['SF2'])
        self.division.CreateRanks(5,self.division.GetGroupsRanks(['H2']))

        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SF1','SF2'])[2:], phase)
        self.division.CreateRanks(3,self.division.GetGroupsRanks(['3rd']))

        # Final
        self.division.CreateGroups(['Final'], self.division.GetGroupsRanks(['SF1','SF2'])[:2], phase)
        self.division.CreateRanks(1,self.division.GetGroupsRanks(['Final']))

    def _addReferees(self):
        """ Referees for  matches """
        self._GroupAddReferees('SF1',[self.division.GetGroupsRanks(['G1'])[0]])
        self._GroupAddReferees('SF2',[self.division.GetGroupsRanks(['G1'])[1]])
        self._GroupAddReferees('H1',[self.division.GetGroupsRanks(['G1'])[2]])
        # self._GroupAddReferees('9th',[ef_ranks[2]])
        # self._GroupAddReferees('7th',[gh_ranks[2]])
        # self._GroupAddReferees('5th',[gh_ranks[0]])
        # self._GroupAddReferees('3rd',[ef_ranks[5]])
        # self._GroupAddReferees('Final',[ef_ranks[4]])
