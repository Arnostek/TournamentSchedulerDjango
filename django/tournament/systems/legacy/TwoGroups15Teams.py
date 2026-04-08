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
        # phase 1 - zakladni skupina
        phase = 1
        self.division.CreateGroups(['A','B'], self.division.seed_placeholders, phase)

        # QF - 1. vs 4., 2. vs 3.
        phase += 1
        self.division.CreateGroups(['QF1','QF2','QF3','QF4'],self.division.GetGroupsRanks(['A','B','C','D'])[:8], phase)

        # SF a Last 3
        phase += 1
        self.division.CreateGroups(['SF1','SF2'],self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[:4], phase)
        self.division.CreateGroups(['SF3','SF4'],self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[4:], phase)

        self.division.CreateGroups(['SF5','SF6'],self.division.GetGroupsRanks(['A','B'])[8:12], phase)

        self.division.CreateGroups(['Last3'],self.division.GetGroupsRanks(['A','B'])[12:], phase)
        self.division.CreateRanks(13,self.division.GetGroupsRanks(['Last3']))

        # Places
        phase += 1
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
