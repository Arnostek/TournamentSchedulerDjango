from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.TwoGroups import TwoGroups
from tournament.systems.MinGames import MinGames16Teams,MinGames6Teams

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2019_5_Pitches'

# turnaj
prague2019 = models.Tournament(name = "Prague 2019 Test 5 hrist cely wait list", slug = "PRG2019T5")
prague2019.save()
####################################################
# men A
MenA_system = TwoGroups(prague2019,'Men A','MenA',12)
MenA_system.division.CreateTeams(
    [
        "Gottingen",
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
        "Vidra A",
    ]
)

####################################################
# men B
MenB_system = MinGames16Teams(prague2019,'Men B','MenB',16)
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
        "KGL Hannover Rodeo Roundhousekick",
        "Prague C",
        "Ukk Wien Men",
        "ASV Horb",
        "Salzburg",
        "Vidra OB",
        "9ValB",
        "KV Nürnberg",
    ]
)

####################################################
# Ladies
Ladies_system = TwoGroups(prague2019,'Ladies','Ladies',12)
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
        "RSV Hannover Women",
        "Muenster",
    ]
)

####################################################
# U14

U14_system = SingleGroupDivisionSystem(prague2019,'U14','U14',7)
U14_system.division.CreateTeams(
    [
        "Dresden U14",
        "Warsawa Powisle U14",
        "Kaniow U14",
        "Glauchau U14",
        "Prague U14",
        "Ukk Wien U14",
        "Kalisz U14",
    ]
)
####################################################
# U16
u16_system = TwoGroups(prague2019,'U16','U16',8)
u16_system.division.CreateTeams(
    [
        "Dresden U16",
        "Warsawa Powisle U16",
        "Glauchau U16",
        "Neuburg U16",
        "Nagymaros U16",
        "Prague U16",
        "Kwisa Lesna U16",
        "Kalisz U16",
    ]
)

## zalozime 4 hriste a prazdny schedule
prague2019.CreatePitches(5)
prague2019.CreateSchedules(datetime.datetime(2019,5,25,7,30),datetime.datetime(2019,5,25,19))
prague2019.CreateSchedules(datetime.datetime(2019,5,26,7,30),datetime.datetime(2019,5,26,15))

## rozhozeni zapasu na hriste

# testovaci kod

# divize Men A na pitch 1
d = MenA_system.division
p = prague2019.pitch_set.all()[0]

for i in range(d.match_set.count()):
    sch = prague2019.schedule_set.filter(pitch = p)[i]
    sch.match = d.match_set.all().order_by('group__phase','phase_block','id')[i]
    sch.save()

# divize Ladies na pitch 2
d = Ladies_system.division
p = prague2019.pitch_set.all()[1]

for i in range(d.match_set.count()):
    sch = prague2019.schedule_set.filter(pitch = p)[i]
    sch.match = d.match_set.all().order_by('group__phase','phase_block','id')[i]
    sch.save()
