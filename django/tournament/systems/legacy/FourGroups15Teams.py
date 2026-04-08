from .DivisionSystemBase import DivisionSystemBase

class FourGroups15Teams(DivisionSystemBase):
    """ 4 zakladni skupiny, QF, SF, umisteni
    """

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(FourGroups15Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - zakladni skupina. Skupiny 4,4,4 a 3
        phase = 1
        self.division.CreateGroups(['A','B','C','D'], self.division.seed_placeholders, phase, ['C','D','A','B'])

        # QF - 1. vs 2., 3. vs 4. + X3
        phase += 1
        # QF ze tretich mist
        self.division.CreateGroups(['EF1','EF2'],self.division.GetGroupsRanks(['A','B','C','D'])[8:12], phase, ['EF1','EF2'],)
        # skupina 4. mist
        self.division.CreateGroups(['E'],self.division.GetGroupsRanks(['A','B','C','D'])[12:], phase, ['E'])
        # QF z prvnich a druhych mist
        self.division.CreateGroups(['QF1','QF2','QF3','QF4'],self.division.GetGroupsRanks(['A','B','C','D'])[:8], phase, ['QF1','QF2','QF3','QF4'])

        # SF + spodek
        phase += 1
        # skupina porazeni dolniho QF a 1. E
        self.division.CreateGroups(['F'],self.division.GetGroupsRanks(['EF1','EF2','E'])[2:5], phase,  ['F'])
        # vitezove dolniho QF
        self.division.CreateGroups(['M1'],self.division.GetGroupsRanks(['EF1','EF2'])[:2], phase)
        # vitezove horniho QF
        self.division.CreateGroups(['SF1','SF2'],self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[:4], phase)
        # porazeni horniho QF
        self.division.CreateGroups(['SF3','SF4'],self.division.GetGroupsRanks(['QF1','QF2','QF3','QF4'])[4:], phase)

        # spodek
        self.division.CreateGroups(['SF5','SF6'],self.division.GetGroupsRanks(['M1','F'])[:4], phase)
        # self.division.CreateGroups(['SF6'],self.division.GetGroupsRanks(['X3','QF6'])[1:3], phase)
        # self.division.CreateGroups(['Last3'],self.division.GetGroupsRanks(['X3','QF5','QF6'])[4:], phase)
        # self.division.CreateGroups(['SF7','SF8'],self.division.GetGroupsRanks(['QF5','QF6','QF7','QF8'])[4:], phase)

        # Places
        phase += 1
        # skupina posledni 3
        self.division.CreateGroups(['Last3'], self.division.GetGroupsRanks(['E','F'])[3:], phase, ['Last3'])
        self.division.CreateRanks(13,self.division.GetGroupsRanks(['Last3']))
        # zapasy o mista
        self.division.CreateGroups(['11th'], self.division.GetGroupsRanks(['SF5','SF6'])[2:], phase)
        self.division.CreateRanks(11,self.division.GetGroupsRanks(['11th']))

        self.division.CreateGroups(['9th'], self.division.GetGroupsRanks(['SF5','SF6'])[:2], phase)
        self.division.CreateRanks(9,self.division.GetGroupsRanks(['9th']))

        self.division.CreateGroups(['7th'], self.division.GetGroupsRanks(['SF3','SF4'])[2:], phase, ['11th'])
        self.division.CreateRanks(7,self.division.GetGroupsRanks(['7th']))

        self.division.CreateGroups(['5th'], self.division.GetGroupsRanks(['SF3','SF4'])[:2], phase, ['9th'])
        self.division.CreateRanks(5,self.division.GetGroupsRanks(['5th']))

        self.division.CreateGroups(['3rd'], self.division.GetGroupsRanks(['SF1','SF2'])[2:], phase, ['7th'])
        self.division.CreateRanks(3,self.division.GetGroupsRanks(['3rd']))

        # Final
        phase += 1
        self.division.CreateGroups(['Final'], self.division.GetGroupsRanks(['SF1','SF2'])[:2], phase, ['5th'])
        self.division.CreateRanks(1,self.division.GetGroupsRanks(['Final']))
        
    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """

        self._GroupAddReferees('EF1',[self.division.GetGroupsRanks(['A', 'B', 'C', 'D'])[4]])
        self._GroupAddReferees('EF2',[self.division.GetGroupsRanks(['A', 'B', 'C', 'D'])[5]])

        self._GroupAddReferees('M1',[self.division.GetGroupsRanks(['EF1', 'B'])[1]])

        self._GroupAddReferees('QF1',[self.division.GetGroupsRanks(['A', 'B', 'C', 'D'])[8]])
        self._GroupAddReferees('QF2',[self.division.GetGroupsRanks(['A', 'B', 'C', 'D'])[9]])
        self._GroupAddReferees('QF3',[self.division.GetGroupsRanks(['A', 'B', 'C', 'D'])[10]])
        self._GroupAddReferees('QF4',[self.division.GetGroupsRanks(['A', 'B', 'C', 'D'])[11]])

        
#        self._GroupAddReferees('11th',[self.division.GetGroupsRanks(['7th'])[0]])
#        self._GroupAddReferees('9th',[self.division.GetGroupsRanks(['7th'])[0]])
        self._GroupAddReferees('SF1',[self.division.GetGroupsRanks(['QF1', 'QF2','QF3', 'QF4' ])[4]])
        self._GroupAddReferees('SF2',[self.division.GetGroupsRanks(['QF1', 'QF2','QF3', 'QF4' ])[5]])
        self._GroupAddReferees('SF3',[self.division.GetGroupsRanks(['QF1', 'QF2','QF3', 'QF4' ])[0]])
        self._GroupAddReferees('SF4',[self.division.GetGroupsRanks(['QF1', 'QF2','QF3', 'QF4' ])[1]])
        self._GroupAddReferees('SF5',[self.division.GetGroupsRanks(['QF1', 'QF2','QF3', 'QF4' ])[2]])
        self._GroupAddReferees('SF6',[self.division.GetGroupsRanks(['QF1', 'QF2','QF3', 'QF4' ])[3]])
        
        self._GroupAddReferees('7th',[self.division.GetGroupsRanks(['11th'])[0]])
        self._GroupAddReferees('5th',[self.division.GetGroupsRanks(['9th'])[0]])
        self._GroupAddReferees('3rd',[self.division.GetGroupsRanks(['7th'])[0]])
        self._GroupAddReferees('Final',[self.division.GetGroupsRanks(['5th'])[0]])
