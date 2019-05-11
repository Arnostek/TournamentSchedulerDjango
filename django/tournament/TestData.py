from . import models
import datetime
from .systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from .systems.TwoGroups import TwoGroups
from .systems.MinGames import MinGames16Teams,MinGames6Teams

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament import TestData'

# turnaj
testTournament = models.Tournament(name = "Prague 2019", slug = "PRG2019")
testTournament.save()
####################################################
# men A
MenA_system = TwoGroups(testTournament,'Men A','MenA',12)
MenA_system.division.CreateTeams(
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

####################################################
# men B
MenB_system = MinGames16Teams(testTournament,'Men B','MenB',16)
MenB_system.division.CreateTeams(
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

####################################################
# Ladies
Ladies_system = TwoGroups(testTournament,'Ladies','Ladies',10)
Ladies_system.division.CreateTeams(
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

####################################################
# U14

U14_system = MinGames6Teams(testTournament,'U14','U14',6)
U14_system.division.CreateTeams(
    [
        "Dresden U14",
        "Warsawa Powisle U14",
        "Kaniow U14",
        "Glauchau U14",
        "Prague U14",
        "Ukk Wien U14",
    ]
)
####################################################
# U16
u16_system = SingleGroupDivisionSystem(testTournament,'U16','U16',7)
u16_system.division.CreateTeams(
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

## zalozime 4 hriste a prazdny schedule
testTournament.CreatePitches(4)
testTournament.CreateSchedules(datetime.datetime(2019,5,29,7),datetime.datetime(2019,5,29,19))
testTournament.CreateSchedules(datetime.datetime(2019,5,30,7),datetime.datetime(2019,5,30,15))

## rozhozeni zapasu na hriste

# testovaci kod

# divize Men A na pitch 1
d = MenA_system.division
p = testTournament.pitch_set.all()[0]

for i in range(d.match_set.count()):
    sch = testTournament.schedule_set.filter(pitch = p)[i]
    sch.match = d.match_set.all().order_by('group__phase','phase_block','id')[i]
    sch.save()

# divize Ladies na pitch 2
d = Ladies_system.division
p = testTournament.pitch_set.all()[1]

for i in range(d.match_set.count()):
    sch = testTournament.schedule_set.filter(pitch = p)[i]
    sch.match = d.match_set.all().order_by('group__phase','phase_block','id')[i]
    sch.save()
