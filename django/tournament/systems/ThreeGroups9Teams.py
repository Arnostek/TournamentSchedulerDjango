from .DivisionSystemBase import DivisionSystemBase
from tournament.models import GroupPointsTransfer

class ThreeGroups9Teams(DivisionSystemBase):
    """ 3 zakladni skupiny, 3 skupiny A1B2C3.., 3 skupiny dle poradi DEF, finale
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
        self.division.CreateGroups(['E'], [self.division.GetGroupsRanks(['A'])[0], self.division.GetGroupsRanks(['B'])[1], self.division.GetGroupsRanks(['C'])[2]], phase, ['E'])
        self.division.CreateGroups(['F'], [self.division.GetGroupsRanks(['B'])[0], self.division.GetGroupsRanks(['C'])[1], self.division.GetGroupsRanks(['A'])[2]], phase, ['F'])
        self.division.CreateGroups(['G'], [self.division.GetGroupsRanks(['C'])[0], self.division.GetGroupsRanks(['A'])[1], self.division.GetGroupsRanks(['B'])[2]], phase, ['G'])

        # skupiny podle poradi
        phase += 1
        self.division.CreateGroups(['J'], self.division.GetGroupsRanks(['E','F','G'])[0:3], phase, ['J'])
        
        self.division.CreateGroups(['K'], self.division.GetGroupsRanks(['E','F','G'])[3:6], phase, ['K'])
        self.division.CreateRanks(5,self.division.GetGroupsRanks(['K'])[1:])
        
        self.division.CreateGroups(['L'], self.division.GetGroupsRanks(['E','F','G'])[6:],  phase, ['L'])
        self.division.CreateRanks(7,self.division.GetGroupsRanks(['L']))

        # # SF pro 1-4
#        phase += 1
#        self.division.CreateGroups(['SF1'], [self.division.GetGroupsRanks(['E'])[0], self.division.GetGroupsRanks(['F'])[0]], phase)
#        self.division.CreateGroups(['SF2'], [self.division.GetGroupsRanks(['E'])[1], self.division.GetGroupsRanks(['E'])[2]], phase)
       
        # places
        phase += 1
        self.division.CreateGroups(['3rd'], [self.division.GetGroupsRanks(['J'])[2], self.division.GetGroupsRanks(['K'])[0]], phase)
        self.division.CreateRanks(3,self.division.GetGroupsRanks(['3rd']))

        # Final
        self.division.CreateGroups(['Final'], self.division.GetGroupsRanks(['J'])[:2], phase)
        self.division.CreateRanks(1,self.division.GetGroupsRanks(['Final']))

    def _addReferees(self):
        """ Referees for  matches """
        self._GroupAddReferees('3rd',[self.division.GetGroupsRanks(['K'])[2]])
        self._GroupAddReferees('Final',[self.division.GetGroupsRanks(['K'])[1]])
