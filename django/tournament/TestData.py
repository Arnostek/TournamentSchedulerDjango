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

    def SeedDivision(self,teams):

        i = 0

        for team_name in teams:
            # najdu TeamPlaceholder
            tph = self.actual_division.divisionseed_set.all()[i].teamPlaceholder
            # vytvorim tym
            team = models.Team(name = team_name)
            team.save()
            # ulozim tym do tph
            tph.team = team
            tph.save()

            i += 1

#    def AddGroups



# turnaj
tdata = TestData("Prague 2019", "PRG2019")
# men A
tdata.AddDivision('Men A','MenA',12)
tdata.actual_division.CreateGroups(['A','B'], tdata.actual_division.seed_placeholders)
#tdata.SeedDivision('Prague A, Prague B, Vidra'.split(','))

# men B
tdata.AddDivision('Men B','MenA',16)
tdata.actual_division.CreateGroups(['A','B','C','D'], tdata.actual_division.seed_placeholders)

# Ladies
tdata.AddDivision('Ladies','Ladies',10)
tdata.actual_division.CreateGroups(['A','B'], tdata.actual_division.seed_placeholders)

# U14
tdata.AddDivision('U14','U14',6)
tdata.actual_division.CreateGroups(['A','B'], tdata.actual_division.seed_placeholders)

# U16
tdata.AddDivision('U16','U16',7)
tdata.actual_division.CreateGroups(['A'], tdata.actual_division.seed_placeholders)
