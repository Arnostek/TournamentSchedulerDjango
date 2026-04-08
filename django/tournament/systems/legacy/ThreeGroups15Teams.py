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
        # phase 1 - zakladni skupina. Skupiny 5,5,5
        phase = 1
        self.division.CreateGroups(['A','B','C'], self.division.seed_placeholders, phase, ['A','B','C'])

        # meziskupiny
        phase += 1
        # 1- 6
        self.division.CreateGroups(['E'], [self.division.GetGroupsRanks(['A'])[0], self.division.GetGroupsRanks(['B'])[1], self.division.GetGroupsRanks(['C'])[0]], phase, ['E'])
        self.division.CreateGroups(['F'], [self.division.GetGroupsRanks(['A'])[1], self.division.GetGroupsRanks(['B'])[0], self.division.GetGroupsRanks(['C'])[1]], phase, ['F'])
        # 7- 12
        self.division.CreateGroups(['G'], [self.division.GetGroupsRanks(['A'])[2], self.division.GetGroupsRanks(['B'])[3], self.division.GetGroupsRanks(['C'])[2]], phase, ['G'])
        self.division.CreateGroups(['H'], [self.division.GetGroupsRanks(['A'])[3], self.division.GetGroupsRanks(['B'])[2], self.division.GetGroupsRanks(['C'])[3]], phase, ['H'])

        # # SF pro 1-4
        phase += 1
        self.division.CreateGroups(['SF1','SF2'], self.division.GetGroupsRanks(['E','F'])[:4], phase)

        # Places
        phase += 1
        # last3
        self.division.CreateGroups(['Last3'],self.division.GetGroupsRanks(['A','B','C'])[12:], phase,['Last3'])
        self.division.CreateRanks(13,self.division.GetGroupsRanks(['Last3']))

        # zapasy o mista
        phase += 1
        self.division.CreateGroups(['11th'], self.division.GetGroupsRanks(['G','H'])[4:6], phase)
        self.division.CreateRanks(11,self.division.GetGroupsRanks(['11th']))

        self.division.CreateGroups(['9th'], self.division.GetGroupsRanks(['G','H'])[2:4], phase)
        self.division.CreateRanks(9,self.division.GetGroupsRanks(['9th']))

        self.division.CreateGroups(['7th'], self.division.GetGroupsRanks(['G','H'])[:2], phase)
        self.division.CreateRanks(7,self.division.GetGroupsRanks(['7th']))

        self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['E','F'])[4:], phase)
        self.division.CreateRanks(5,self.division.GetGroupsRanks(['5th']))

        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SF1','SF2'])[2:], phase)
        self.division.CreateRanks(3,self.division.GetGroupsRanks(['3rd']))

        # Final
        phase += 1
        self.division.CreateGroups(['Final'], self.division.GetGroupsRanks(['SF1','SF2'])[:2], phase)
        self.division.CreateRanks(1,self.division.GetGroupsRanks(['Final']))

    def _addReferees(self):
        """ Referees for  matches """
        gh_ranks = self.division.GetGroupsRanks(['G','H'])
        ef_ranks = self.division.GetGroupsRanks(['E','F'])
        self._GroupAddReferees('SF1',[ef_ranks[4]])
        self._GroupAddReferees('SF2',[ef_ranks[5]])
        self._GroupAddReferees('11th',[ef_ranks[3]])
        self._GroupAddReferees('9th',[ef_ranks[2]])
        self._GroupAddReferees('7th',[gh_ranks[2]])
        self._GroupAddReferees('5th',[gh_ranks[0]])
        self._GroupAddReferees('3rd',[ef_ranks[5]])
        self._GroupAddReferees('Final',[ef_ranks[4]])
