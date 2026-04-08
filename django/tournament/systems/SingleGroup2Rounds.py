from .DivisionSystemBase import DivisionSystemBase
from tournament.models import GroupPointsTransfer
import random

class SingleGroup2Rounds(DivisionSystemBase):
    """ Jedna zakladni skupina, kazdy s kazdym, zapas o 3. a prvni misto """

    def __init__(self,tournament,division_name,division_slug,num_of_teams,semi = False, add_referees = True):
        # zavolam konsturktor Predka
        super(SingleGroup2Rounds, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = False, add_referees = add_referees)
        # create game system
        self._createSystem()
        # generate matches
        self._createMatches()
        # add referees
        self._addReferees()

    def _createSystem(self):
        # phase 1 - first round
        self.phase.create_groups(['R1'], self.division.seed_placeholders, referee_groups=['R1'])

        # phase 2 - second round
        self.phase.next_phase()
        self.phase.create_groups(['R2'], self.division.seed_placeholders, referee_groups=['R2'])

        r2_ranks = self.phase.get_ranks(['R2'])
        # transfer points from R1 to R2
        GroupPointsTransfer.objects.create(src = self.division.GetGroup('R1'), dest = self.division.GetGroup('R2'))

        # 3rd
        if self.teams_count > 3:
            self.phase.next_phase()
            self.phase.create_and_rank('3rd', [r2_ranks[2], r2_ranks[3]], 3)

        # final
        self.phase.next_phase()
        self.phase.create_and_rank('final', [r2_ranks[0], r2_ranks[1]], 1)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        if self.add_referees:
            r2_ranks = self.phase.get_ranks(['R2'])
            self.referees.assign_multiple_referees({
                '3rd': [r2_ranks[1]],
                'final': [r2_ranks[2]],
            })
