from .DivisionSystemBase import DivisionSystemBase
from tournament.models import GroupPointsTransfer

class MinGames16Teams(DivisionSystemBase):
    """ 4 zakladni skupiny, pak rozdeleno na horni a dolni kde kazdy odehraje prave jeden zapas. Pricitaji se body z minule. Semi a zapasy o misto."""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(MinGames16Teams, self).__init__(tournament,division_name,division_slug,num_of_teams,semi = True)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()
        # doplnime rozhodci
        self._addReferees()

    def _createSystem(self):
        # phase 1 - zakladni skupiny
        self.phase.create_groups(
            ['A','B','C','D'],
            self.division.seed_placeholders,
            referee_groups=['C','D','A','B']
        )
        phase1_ranks = self.phase.get_ranks(['A','B','C','D'])

        # dolni a horni skupina, kde kazdy hraje jednou, zapasy vygenerujeme rucne
        self.phase.next_phase()
        self.phase.create_groups(['E'], phase1_ranks[:8])
        e_group = self.division.group_set.last()
        self.phase.create_groups(['F'], phase1_ranks[8:])
        f_group = self.division.group_set.last()

        # do E a F prenasime body z minula
        GroupPointsTransfer.objects.create(src = self.division.GetGroup('A'), dest = self.division.GetGroup('E'))
        GroupPointsTransfer.objects.create(src = self.division.GetGroup('B'), dest = self.division.GetGroup('E'))
        GroupPointsTransfer.objects.create(src = self.division.GetGroup('C'), dest = self.division.GetGroup('E'))
        GroupPointsTransfer.objects.create(src = self.division.GetGroup('D'), dest = self.division.GetGroup('E'))

        GroupPointsTransfer.objects.create(src = self.division.GetGroup('A'), dest = self.division.GetGroup('F'))
        GroupPointsTransfer.objects.create(src = self.division.GetGroup('B'), dest = self.division.GetGroup('F'))
        GroupPointsTransfer.objects.create(src = self.division.GetGroup('C'), dest = self.division.GetGroup('F'))
        GroupPointsTransfer.objects.create(src = self.division.GetGroup('D'), dest = self.division.GetGroup('F'))

        # zapasy skupin E a F
        e_group.CreateMatch((2,7,3))
        f_group.CreateMatch((2,7,3))
        e_group.CreateMatch((3,6,3))
        f_group.CreateMatch((3,6,3))
        e_group.CreateMatch((1,8,3))
        f_group.CreateMatch((1,8,3))
        e_group.CreateMatch((4,5,3))
        f_group.CreateMatch((4,5,3))
        # semi - prvni 4 tymy z horni skupiny
        self.phase.next_phase()
        self.phase.create_groups(['SemiA','SemiB'], self.phase.get_ranks(['E'])[:4])

        # zapasy o mista bez semi
        self.phase.next_phase()
        f_ranks = self.phase.get_ranks(['F'])
        e_ranks = self.phase.get_ranks(['E'])

        # Create placement matches with ranks
        for misto in [15,13,11,9]:
            self.division.CreateGroups(['{}th'.format(misto)], f_ranks[misto - 9: misto -7], self.phase.phase)
            self.division.CreateRanks(misto, self.division.GetGroupsRanks(['{}th'.format(misto)]))

        for misto in [7,5]:
            self.division.CreateGroups(['{}th'.format(misto)], e_ranks[misto - 1: misto + 1], self.phase.phase)
            self.division.CreateRanks(misto, self.division.GetGroupsRanks(['{}th'.format(misto)]))

        # 3rd
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', self.phase.get_ranks(['SemiA','SemiB'])[2:4], 3)

        # final
        self.phase.next_phase()
        self.phase.create_and_rank('final', self.phase.get_ranks(['SemiA','SemiB'])[0:2], 1)

    def _addReferees(self):
        """ Doplneni rozhodcich pro finalove zapasy """
        # gropy E a F
        phase1_ranks = self.phase.get_ranks(['A','B','C','D'])
        self.referees.assign_multiple_referees({
            'E': [phase1_ranks[0],phase1_ranks[1],phase1_ranks[2],phase1_ranks[3]],
            'F': [phase1_ranks[8],phase1_ranks[9],phase1_ranks[10],phase1_ranks[11]],
        })

        # Semi
        groupE_ranks = self.phase.get_ranks(['E'])
        groupF_ranks = self.phase.get_ranks(['F'])
        self.referees.assign_multiple_referees({
            'SemiA': [groupE_ranks[4]],
            'SemiB': [groupE_ranks[5]],
        })

        # umisteni
        self.referees.assign_multiple_referees({
            '15th': [groupF_ranks[0]],
            '13th': [groupF_ranks[1]],
            '11th': [groupF_ranks[7]],
            '9th': [groupF_ranks[6]],
            '7th': [groupF_ranks[4]],
            '5th': [self.division.GetGroupsRanks(['11th'])[0]],
            '3rd': [self.division.GetGroupsRanks(['9th'])[0]],
            'final': [self.division.GetGroupsRanks(['7th'])[0]],
        })


class MinGames6Teams(DivisionSystemBase):
    """ 2 zakladni skupiny, pak jedna velka skupina kde kazdy odehraje dva zapasy. Pricitaji se body z minule. Nasleduji zapasy o misto."""

    def __init__(self,tournament,division_name,division_slug,num_of_teams):
        # zavolam konsturktor Predka
        super(MinGames6Teams, self).__init__(tournament,division_name,division_slug,num_of_teams)
        # vytvorim system
        self._createSystem()
        # vygeneruji zapasy
        self._createMatches()

    def _createSystem(self):
        self.phase.create_groups(['A','B'], self.division.seed_placeholders)
        # skupina, kde se neodehraje vsechno, zapasy vygenerujeme rucne
        self.phase.next_phase()
        self.phase.create_groups(['C'], self.phase.get_ranks(['A','B']))
        c_group = self.division.group_set.last()
        c_group.CreateMatch((1,4,0))
        c_group.CreateMatch((3,6,0))
        c_group.CreateMatch((5,2,0))
        c_group.CreateMatch((1,6,1))
        c_group.CreateMatch((3,2,1))
        c_group.CreateMatch((5,4,1))

        #5th
        self.phase.next_phase()
        self.phase.create_and_rank('5th', self.phase.get_ranks(['C'])[4:6], 5)

        # 3rd
        self.phase.next_phase()
        self.phase.create_and_rank('3rd', self.phase.get_ranks(['C'])[2:4], 3)

        # final
        self.phase.next_phase()
        self.phase.create_and_rank('final', self.phase.get_ranks(['C'])[0:2], 1)

        # vygenerovani zapasu
        self.division.CreateMatches()
