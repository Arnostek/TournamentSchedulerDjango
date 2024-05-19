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

    def _createSystem(self):
        # phase 1 - zakladni skupina. Skupiny 5,5,5
        phase = 1
        self.division.CreateGroups(['A','B','C'], self.division.seed_placeholders, phase)

        # meziskupiny pro 2. a 3.
        phase += 1
        self.division.CreateGroups(['E'], self.division.GetGroupsRanks(['A','B','C'])[3:6], phase)
        self.division.CreateGroups(['F'], self.division.GetGroupsRanks(['A','B','C'])[6:9], phase)

        # QF pro 1-8
        phase += 1
        self.division.CreateGroups(['QF1'], [self.division.GetGroupsRanks(['A'])[0], self.division.GetGroupsRanks(['F'])[1]], phase)
        self.division.CreateGroups(['QF2'], [self.division.GetGroupsRanks(['B'])[0], self.division.GetGroupsRanks(['F'])[0]], phase)
        self.division.CreateGroups(['QF3'], [self.division.GetGroupsRanks(['C'])[0], self.division.GetGroupsRanks(['E'])[2]], phase)
        self.division.CreateGroups(['QF4'], [self.division.GetGroupsRanks(['E'])[0], self.division.GetGroupsRanks(['E'])[1]], phase)

        # SF a Last3
        phase += 1
        # SF 8-12
        self.division.CreateGroups(['SF5'], [self.division.GetGroupsRanks(['F'])[2], self.division.GetGroupsRanks(['C'])[3]], phase)
        self.division.CreateGroups(['SF6'], [self.division.GetGroupsRanks(['A'])[3], self.division.GetGroupsRanks(['B'])[3]], phase)
        # porazeni horniho QF
        self.division.CreateGroups(['SF3','SF4'],self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[4:], phase)
        # vitezove horniho QF
        self.division.CreateGroups(['SF1','SF2'],self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[:4], phase)

        # Places
        phase += 1
        # last3
        self.division.CreateGroups(['Last3'],self.division.GetGroupsRanks(['A','B','C'])[12:], phase)
        self.division.CreateRanks(13,self.division.GetGroupsRanks(['Last3']))

        # zapasy o mista
        self.division.CreateGroups(['11th'], self.division.GetGroupsRanks(['SF5','SF6'])[2:], phase)
        self.division.CreateRanks(11,self.division.GetGroupsRanks(['11th']))

        self.division.CreateGroups(['9th'], self.division.GetGroupsRanks(['SF5','SF6'])[:2], phase)
        self.division.CreateRanks(9,self.division.GetGroupsRanks(['9th']))

        self.division.CreateGroups(['7th'], self.division.GetGroupsRanks(['SF3','SF4'])[2:], phase)
        self.division.CreateRanks(7,self.division.GetGroupsRanks(['7th']))

        self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['SF3','SF4'])[:2], phase)
        self.division.CreateRanks(5,self.division.GetGroupsRanks(['5th']))

        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SF1','SF2'])[2:], phase)
        self.division.CreateRanks(3,self.division.GetGroupsRanks(['3rd']))

        # Final
        phase += 1
        self.division.CreateGroups(['Final'], self.division.GetGroupsRanks(['SF1','SF2'])[:2], phase)
        self.division.CreateRanks(1,self.division.GetGroupsRanks(['Final']))

