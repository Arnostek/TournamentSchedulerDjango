from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.SingleGroup5teams import SingleGroup5teams
from tournament.systems.TwoGroups import TwoGroups
from tournament.TournamentScheduler import TournamentScheduler

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2020_3_Pitches'

# turnaj
prague2022 = models.Tournament(name = "PIT 2022", slug = "PIT2022")
prague2022.save()
print(prague2022)
####################################################
# men 1
Men1_system = TwoGroups(prague2022,'Men 1','Men1',11,last3=True)
Men1_system.division.CreateTeams(
    [
        "Goettingen A",
        "KG Wanderfalke Essen",
        "Katowice Men",
        "Kaniow Men",
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
# men 2
Men2_system = TwoGroups(prague2022,'Men 2','Men2',11,last3=True)
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
    ]
)


####################################################
# U15

U15_system = SingleGroupDivisionSystem(prague2022,'U15','U15',6)
U15_system.division.CreateTeams(
    [
        "VMW Berlin U14",
        "Katowice U15",
        "Dresden U15-1",
        "Dresden U15-2",
        "Prague U15 M",
        "Prague U15 W",
    ]
)

####################################################
# U18

U18_system = SingleGroup5teams(prague2022,'U18','U18',5)
U18_system.division.CreateTeams(
    [
        "UKK Wien U18",
        "Kaniow U16",
        "Kalisz U18",
        "Kalisz U16",
        "Czech U18",
    ]
)

####################################################
# Ladies
Ladies_system = SingleGroupDivisionSystem(prague2022,'Ladies','Ladies',7,semi=False)
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
# ts.schedule.dropna(inplace=True, how='all')
ts._reduceEmptySlots(35)
ts._reduceEmptySlots(35)
ts._reduceEmptySlots(35)
# ts._reduceEmptySlots02(35)
# ts._reduceEmptySlots03(35)
# ts._reduceEmptySlots02(33)

ts.Schedule(
    [
        (datetime.datetime(2022,5,28,7,30),datetime.datetime(2022,5,28,18,30)),
        (datetime.datetime(2022,5,29,8,00),datetime.datetime(2022,5,29,23))
    ]
)
