from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.TwoGroups import TwoGroups
from tournament.systems.MinGames import MinGames16Teams,MinGames6Teams
from tournament.TournamentScheduler import TournamentScheduler

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

## naplanujeme zapasy

ts = TournamentScheduler(prague2019,5)
ts.Schedule(
    [
        (datetime.datetime(2019,5,25,7),datetime.datetime(2019,5,25,21)),
        (datetime.datetime(2019,5,26,7),datetime.datetime(2019,5,26,21))
    ]
)
