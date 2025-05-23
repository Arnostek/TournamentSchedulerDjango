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
        phase = 1
        self.division.CreateGroups(['A','B','C','D'], self.division.seed_placeholders, phase, ['C','D','A','B'])

        # QF - 1. vs 2., 3. vs 4.
        phase += 1
        self.division.CreateGroups(['QF1','QF2','QF3','QF4'],self.division.GetGroupsRanks(['A','B','C','D'])[8:], phase)
        self.division.CreateGroups(['QF5','QF6','QF7','QF8'],self.division.GetGroupsRanks(['A','B','C','D'])[:8], phase)

        # SF
        phase += 1
        self.division.CreateGroups(['SF1','SF2'],self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[:4], phase)
        self.division.CreateGroups(['SF3','SF4'],self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[4:], phase)
        self.division.CreateGroups(['SF5','SF6'],self.division.GetGroupsRanks(['QF5','QF6','QF7','QF8'])[:4], phase)
        self.division.CreateGroups(['SF7','SF8'],self.division.GetGroupsRanks(['QF5','QF6','QF7','QF8'])[4:], phase)

        # Places
        phase += 1
        self.division.CreateGroups(['15th'], self.division.GetGroupsRanks(['SF7','SF8'])[2:], phase)
        self.division.CreateRanks(15,self.division.GetGroupsRanks(['15th']))

        self.division.CreateGroups(['13th'], self.division.GetGroupsRanks(['SF7','SF8'])[:2], phase)
        self.division.CreateRanks(13,self.division.GetGroupsRanks(['13th']))

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
