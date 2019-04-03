from . import models
import datetime

# run it in shell by:
# from tournament.TestData import TestData

# zakladani testovacich dat
class TestData:

    def __init__(self, tournamentName, tournamentSlug):

        self.t = models.Tournament()
        self.t.name = tournamentName
        self.t.slug = tournamentSlug
        self.t.save()

    def AddDivision(self, name, slug, teams_count):

        self.actual_division = self.t.division_set.create(name = name, slug = slug, teams = teams_count)

# turnaj
tdata = TestData("Prague 2019", "PRG2019")
####################################################
# men A
tdata.AddDivision('Men A','MenA',12)
tdata.actual_division.CreateTeams(
    [
        "Gottingen",
        "KV Nürnberg",
        "Warsawa Powisle Men",
        "Kaniow Men",
        "Neuburg Men",
        "Prague A",
        "Prague B",
        "Austria Men",
        "KTW Kalisz",
        "RKV Berlin",
        "Kwisa Lesna Men",
        "9ValA",
    ]
)
# zakladani skupiny
tdata.actual_division.CreateGroups(['A','B'], tdata.actual_division.seed_placeholders, 1)
# prvni 4 jdou do semi
tdata.actual_division.CreateGroups(['SemiA','SemiB'], tdata.actual_division.GetGroupsRanks(['A','B'])[:4], 2)
# zapasy o mista bez semi
for misto in [11,9,7,5]:
    tdata.actual_division.CreateGroups(['{}th'.format(misto)], tdata.actual_division.GetGroupsRanks(['A','B'])[misto - 1: misto + 1], 3)
# 3rd
tdata.actual_division.CreateGroups(['3rd'], tdata.actual_division.GetGroupsRanks(['SemiA','SemiB'])[2:4], 4)
# final
tdata.actual_division.CreateGroups(['final'], tdata.actual_division.GetGroupsRanks(['SemiA','SemiB'])[0:2], 5)
# vygenerovani zapasu
tdata.actual_division.CreateMatches()

####################################################
# men B
tdata.AddDivision('Men B','MenB',16)
tdata.actual_division.CreateTeams(
    [
        "Dresden Men",
        "Leipzig Men",
        "Glauchau Men",
        "Kelheim Men",
        "Schleißheimer Men",
        "Nagymaros Men",
        "Pirates from Bergheim A",
        "Pirates from Bergheim B",
        "Linz",
        "KGL Hannover Rodeo Roundhousekick",
        "Prague C",
        "Ukk Wien Men",
        "ASV Horb",
        "Salzburg",
        "Vidra OB",
        "9ValB",
    ]
)
tdata.actual_division.CreateGroups(['A','B','C','D'], tdata.actual_division.seed_placeholders, 1)
# skupina, kde kazdy hraje jednou, zapasy vygenerujeme rucne
tdata.actual_division.CreateGroups(['E'], tdata.actual_division.GetGroupsRanks(['A','B','C','D']), 2)
e_group = tdata.actual_division.group_set.last()
e_group.CreateMatch((1,16,3))
e_group.CreateMatch((2,15,3))
e_group.CreateMatch((3,14,3))
e_group.CreateMatch((4,13,3))
e_group.CreateMatch((5,12,3))
e_group.CreateMatch((6,11,3))
e_group.CreateMatch((7,10,3))
e_group.CreateMatch((8,9,3))
# semi
tdata.actual_division.CreateGroups(['SemiA','SemiB'], tdata.actual_division.GetGroupsRanks(['E'])[:4], 3)
# o mista

for misto in [15,13,11,9,7,5]:
    tdata.actual_division.CreateGroups(['{}th'.format(misto)], tdata.actual_division.GetGroupsRanks(['E'])[misto - 1: misto + 1], 4)
# 3rd
tdata.actual_division.CreateGroups(['3rd'], tdata.actual_division.GetGroupsRanks(['SemiA','SemiB'])[2:4], 5)
# final
tdata.actual_division.CreateGroups(['final'], tdata.actual_division.GetGroupsRanks(['SemiA','SemiB'])[0:2], 6)
# vygenerovani zapasu
tdata.actual_division.CreateMatches()

####################################################
# Ladies
tdata.AddDivision('Ladies','Ladies',10)
tdata.actual_division.CreateTeams(
    [
        "Havelbrüder Berlin",
        "Leipzig Women",
        "Warsawa Powisle Women",
        "Kaniow Women",
        "Neuburg Women",
        "Nagymaros Women",
        "Heidelberg Women",
        "Prague Women",
        "Swiss Dream Team",
        "Ukk Wien Women",
    ]
)
tdata.actual_division.CreateGroups(['A','B'], tdata.actual_division.seed_placeholders, 1)
tdata.actual_division.CreateGroups(['SemiA','SemiB'], tdata.actual_division.GetGroupsRanks(['A','B'])[:4], 2)

# zapasy o mista bez semi
for misto in [9,7,5]:
    tdata.actual_division.CreateGroups(['{}th'.format(misto)], tdata.actual_division.GetGroupsRanks(['A','B'])[misto - 1: misto + 1], 3)
# 3rd
tdata.actual_division.CreateGroups(['3rd'], tdata.actual_division.GetGroupsRanks(['SemiA','SemiB'])[2:4], 4)
# final
tdata.actual_division.CreateGroups(['final'], tdata.actual_division.GetGroupsRanks(['SemiA','SemiB'])[0:2], 5)
# vygenerovani zapasu
tdata.actual_division.CreateMatches()
####################################################
# U14
tdata.AddDivision('U14','U14',6)
tdata.actual_division.CreateTeams(
    [
        "Dresden U14",
        "Warsawa Powisle U14",
        "Kaniow U14",
        "Glauchau U14",
        "Prague U14",
        "Ukk Wien U14",
    ]
)
tdata.actual_division.CreateGroups(['A','B'], tdata.actual_division.seed_placeholders, 1)
# skupina, kde se neodehraje vsechno, zapasy vygenerujeme rucne
tdata.actual_division.CreateGroups(['C'], tdata.actual_division.GetGroupsRanks(['A','B']), 2)
c_group = tdata.actual_division.group_set.last()
c_group.CreateMatch((1,4,0))
c_group.CreateMatch((3,6,0))
c_group.CreateMatch((5,2,0))
c_group.CreateMatch((1,6,1))
c_group.CreateMatch((3,2,1))
c_group.CreateMatch((5,4,1))

#5th
tdata.actual_division.CreateGroups(['5th'], tdata.actual_division.GetGroupsRanks(['C'])[4:6], 3)
# 3rd
tdata.actual_division.CreateGroups(['3rd'], tdata.actual_division.GetGroupsRanks(['C'])[2:4], 4)
# final
tdata.actual_division.CreateGroups(['final'], tdata.actual_division.GetGroupsRanks(['C'])[0:2], 5)
# vygenerovani zapasu
tdata.actual_division.CreateMatches()
####################################################
# U16
tdata.AddDivision('U16','U16',7)
tdata.actual_division.CreateTeams(
    [
        "Dresden U16",
        "Warsawa Powisle U16",
        "Glauchau U16",
        "Neuburg U16",
        "Nagymaros U16",
        "Prague U16",
        "Kwisa Lesna U16",
    ]
)
tdata.actual_division.CreateGroups(['A'], tdata.actual_division.seed_placeholders, 1)

a_ranks = tdata.actual_division.GetGroupsRanks(['A'])
# 3rd
tdata.actual_division.CreateGroups(['3rd'], [a_ranks[2], a_ranks[3]] , 2)
# final
tdata.actual_division.CreateGroups(['final'],[a_ranks[0], a_ranks[1]] , 3)
# vygenerovani zapasu
tdata.actual_division.CreateMatches()

## zalozime 4 hriste a prazdny schedule
tdata.CreatePitches(4)
tdata.CreateSchedules(datetime.datetime(2019,5,29,7),datetime.datetime(2019,5,29,19))
tdata.CreateSchedules(datetime.datetime(2019,5,30,7),datetime.datetime(2019,5,30,15))
