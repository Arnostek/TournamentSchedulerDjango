from . import models

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
# vygenerovani zapasu
tdata.actual_division.CreateMatches()

####################################################
# Ladies
tdata.AddDivision('Ladies','Ladies',10)
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
tdata.actual_division.CreateGroups(['A','B'], tdata.actual_division.seed_placeholders, 1)
# vygenerovani zapasu
tdata.actual_division.CreateMatches()
####################################################
# U16
tdata.AddDivision('U16','U16',7)
tdata.actual_division.CreateGroups(['A'], tdata.actual_division.seed_placeholders, 1)
# vygenerovani zapasu
tdata.actual_division.CreateMatches()
