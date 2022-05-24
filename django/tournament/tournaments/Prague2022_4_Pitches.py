from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.SingleGroup5teams import SingleGroup5teams
from tournament.systems.TwoGroups import TwoGroups
from tournament.systems.TwoGroups8Teams import TwoGroups8Teams
from tournament.systems.FourGroups12Teams import FourGroups12Teams
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
Men1_system = TwoGroups(prague2022,'Men Elite','MenElite',10,last3=False,semi5_8=True)
Men1_system.division.CreateTeams(
    [
        "RKV Berlin",
        "KCNW Berlin",
        "KG Wanderfalke Essen",
        "Czech U21",
        "Goettingen A",
        "Prague A",
        "Wien Men",
        # "Kaniow Men",
        "Nuremberg Men",
        "Kalisz Men",
        "Katowice Men",
    ]
)

####################################################
# Ladies
Ladies_system = SingleGroupDivisionSystem(prague2022,'Ladies','Ladies',7,semi=False,final_for=1)
Ladies_system.division.CreateTeams(
    [
        "Goettingen Women",
        "SG Jambalaya",
        "VMW Berlin Women",
        "Kaniow Women",
        "Dresden Women",
        "Prague Women",
        "Prague U18 Women",
    ]
)

####################################################
# men 2
Men2_system = FourGroups12Teams(prague2022,'Men 2','Men2',12)
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
        "DobroPtaah",
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
        "Kwisa Lesna U18",

    ]
)

####################################################
# U15

U15_system = TwoGroups8Teams(prague2022,'U15','U15',8)
U15_system.division.CreateTeams(
    [
        "VMW Berlin U14",
        "Katowice U15",
        "Dresden U15-1",
        "Dresden U15-2",
        "Prague U15 M-1",
        "Prague U15 M-2",
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
ts.tdo._reduceEmptySlots01(36)
ts.tdo._reduceEmptySlots02(36)
ts.tdo._reduceEmptySlots03(36)

ts.Schedule(
    [
        (datetime.datetime(2022,5,28,7,00,tzinfo = pytz.utc),datetime.datetime(2022,5,28,19,00,tzinfo = pytz.utc)),
        (datetime.datetime(2022,5,29,7,30,tzinfo = pytz.utc),datetime.datetime(2022,5,29,23,tzinfo = pytz.utc)),
        # (datetime.datetime(2022,5,30,7,30),datetime.datetime(2022,5,30,23)),
    ]
)
