from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.SingleGroup5teams import SingleGroup5teams
from tournament.systems.TwoGroups import TwoGroups
from tournament.systems.FourGroups13Teams import FourGroups13Teams
from tournament.TournamentScheduler import TournamentScheduler
import pytz

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2020_3_Pitches'

# turnaj
prague2022 = models.Tournament(name = "PIT 2022", slug = "PIT2022")
prague2022.save()
print(prague2022)
####################################################
# men 1
Men1_system = TwoGroups(prague2022,'Men 1','Men1',10,last3=False)
Men1_system.division.CreateTeams(
    [
        "Goettingen A",
        "KG Wanderfalke Essen",
        "Katowice Men",
        # "Kaniow Men",
        "Nuremberg Men",
        "Wien Men",
        "RKV Berlin",
        "Kalisz Men",
        "KCNW Berlin",
        "Prague A",
        "Czech U21",
    ]
)

####################################################
# Ladies
Ladies_system = SingleGroupDivisionSystem(prague2022,'Ladies','Ladies',7,semi=False,final_for=1)
Ladies_system.division.CreateTeams(
    [
        "Goettingen Women",
        "Spielgemeinschaft (SG) Jambalaya",
        "VMW Berlin Women",
        "Kaniow Women",
        "Dresden Women",
        "Prague Women",
        "Prague U18 Women",
    ]
)

####################################################
# men 2
Men2_system = FourGroups13Teams(prague2022,'Men 2','Men2',13)
Men2_system.division.CreateTeams(
    [
        "Goettingen B",
        "KC Kelheim",
        "SG Potsdam",
        "Leipzig",
        "WCH Berlin",
        "Kwisa Lesna",
        "VMW Berlin Men",
        "Jägi Berlin",
        "Dresden Men",
        "KGL Hannover",
        "Dobroptaah",
        "Denmark U18",
        "Schleißheimer PC",
    ]
)

####################################################
# U18

U18_system = SingleGroupDivisionSystem(prague2022,'U18','U18',7,semi=False,final_for=1)
U18_system.division.CreateTeams(
    [
        "UKK Wien U18",
        "Kaniow U16",
        "Kalisz U18",
        "Kalisz U16",
        "Czech U18",
        "Kalisz U16 Girls",
        "Kwisa Leszna U18",

    ]
)

####################################################
# U15

U15_system = SingleGroupDivisionSystem(prague2022,'U15','U15',7,semi=False,final_for=1)
U15_system.division.CreateTeams(
    [
        "VMW Berlin U14",
        "Katowice U15",
        "Dresden U15-1",
        "Dresden U15-2",
        "Prague U15 M",
        "Prague U15 W",
        "Kwisa Leszna U15",
    ]
)

####################################################
# Domca

# Domca_system = SingleGroupDivisionSystem(prague2022,'Special','Special',2)
# Domca_system.division.CreateTeams(
#     [
#         "Stary holky",
#         "Maldy holky",
#     ]
# )


## naplanujeme zapasy

ts = TournamentScheduler(prague2022,4)

# optimize pitches
# ts.tdo._reduceColumns(ts.pitches)
ts.tdo._reduceColumnsOnePitch(ts.pitches)
# add referees
ts.AddReferees()
# ts.schedule.dropna(inplace=True, how='all')

# optimize games
ts.tdo._reduceEmptySlots01(38)
ts.tdo._reduceEmptySlots02(38)
ts.tdo._reduceEmptySlots03(38)

ts.Schedule(
    [
        (datetime.datetime(2022,5,28,7,00,tzinfo = pytz.utc),datetime.datetime(2022,5,28,19,00,tzinfo = pytz.utc)),
        (datetime.datetime(2022,5,29,7,00,tzinfo = pytz.utc),datetime.datetime(2022,5,29,23,tzinfo = pytz.utc)),
        # (datetime.datetime(2022,5,30,7,30),datetime.datetime(2022,5,30,23)),
    ]
)
