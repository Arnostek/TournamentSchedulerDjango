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
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - zakladni skupina
        phase = 1
        self.division.CreateGroups(['A','B','C','D'], self.division.seed_placeholders, phase, ['C','D','A','B'])

        # QF - 1. vs 2., 3. vs 4.
        phase += 1
        self.division.CreateGroups(['QF1','QF2','QF3','QF4'],self.division.GetGroupsRanks(['A','B','C','D'])[:8], phase)
        self.division.CreateGroups(['QF5','QF6','QF7','QF8'],self.division.GetGroupsRanks(['A','B','C','D'])[8:], phase)

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

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """

        # horni QF piska 3. ze skupin
        self._GroupAddReferees('QF1',[self.division.GetGroupsRanks(['A'])[2]])
        self._GroupAddReferees('QF2',[self.division.GetGroupsRanks(['B'])[2]])
        self._GroupAddReferees('QF3',[self.division.GetGroupsRanks(['C'])[2]])
        self._GroupAddReferees('QF4',[self.division.GetGroupsRanks(['D'])[2]])

        # dolni QF piska 2. ze skupin
        self._GroupAddReferees('QF5',[self.division.GetGroupsRanks(['D'])[1]])
        self._GroupAddReferees('QF6',[self.division.GetGroupsRanks(['C'])[1]])
        self._GroupAddReferees('QF7',[self.division.GetGroupsRanks(['B'])[1]])
        self._GroupAddReferees('QF8',[self.division.GetGroupsRanks(['A'])[1]])

        # SF 1-4
        self._GroupAddReferees('SF1',[self.division.GetGroupsRanks(['QF1'])[1]])
        self._GroupAddReferees('SF2',[self.division.GetGroupsRanks(['QF2'])[1]])
        # SF 5-8
        self._GroupAddReferees('SF3',[self.division.GetGroupsRanks(['QF1'])[0]])
        self._GroupAddReferees('SF4',[self.division.GetGroupsRanks(['QF2'])[0]])
        # SF 9-12
        self._GroupAddReferees('SF5',[self.division.GetGroupsRanks(['QF4'])[1]])
        self._GroupAddReferees('SF6',[self.division.GetGroupsRanks(['QF3'])[1]])
        # SF 13-16
        self._GroupAddReferees('SF7',[self.division.GetGroupsRanks(['QF4'])[0]])
        self._GroupAddReferees('SF8',[self.division.GetGroupsRanks(['QF3'])[0]])

        # mista
        self._GroupAddReferees('15th',[self.division.GetGroupsRanks(['SF3'])[1]])
        self._GroupAddReferees('13th',[self.division.GetGroupsRanks(['SF4'])[1]])
        self._GroupAddReferees('11th',[self.division.GetGroupsRanks(['SF3'])[0]])
        self._GroupAddReferees('9th',[self.division.GetGroupsRanks(['SF4'])[0]])
        self._GroupAddReferees('7th',[self.division.GetGroupsRanks(['SF3'])[0]])
        self._GroupAddReferees('5th',[self.division.GetGroupsRanks(['11th'])[0]])
        self._GroupAddReferees('3rd',[self.division.GetGroupsRanks(['5th'])[1]])
        self._GroupAddReferees('Final',[self.division.GetGroupsRanks(['5th'])[0]])
