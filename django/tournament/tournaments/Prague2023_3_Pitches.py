from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.SingleGroup2Rounds import SingleGroup2Rounds
from tournament.systems.TwoGroups import TwoGroups
from tournament.systems.TwoGroups8Teams import TwoGroups8Teams
from tournament.systems.FourGroups12Teams import FourGroups12Teams
from tournament.TournamentScheduler import TournamentScheduler
import pytz

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2020_3_Pitches'

# turnaj
prague2023 = models.Tournament(name = "PIT 2023 TEST", slug = "PIT2023-TEST26")
prague2023.save()
print(prague2023)
####################################################
# men 1
Men1_system = TwoGroups(prague2023,'Men Elite','MenElite',8,semi5_8=True)
Men1_system.division.CreateTeams(
    [
"UKS Katowice Men",
"KTW 1",
"Prague A",
"Prague B",
"Czech U21",
"Trakai",
"Lesna Men",
"Austria U21",
        # "RKV Berlin",
        # "KCNW Berlin",
        # "KG Wanderfalke Essen",
        # "Czech U21",
        # "Goettingen A",
        # "Prague A",
        # "Wien Men",
        # # "Kaniow Men",
        # "Nuremberg Men",
        # "Kalisz Men",
        # "Katowice Men",
    ]
)

####################################################
# Ladies
Ladies_system = TwoGroups(prague2023,'Ladies','Ladies',8,semi5_8=True)
Ladies_system.division.CreateTeams(
    [
        "VMW Berlin Women",
        "KSVH Berlin Women",
        "UKS Kaniow Women",
        "UKS Katowice Women",
        "Austria Women",
        "Dresden Women",
        "Czech U21 Women",
        "Prague Women",

        # "Goettingen Women",
        # "SG Jambalaya",
        # "VMW Berlin Women",
        # "Kaniow Women",
        # "Dresden Women",
        # "Prague Women",
        # "Czech U18 Women",
    ]
)

####################################################
# U15

U15_system = TwoGroups(prague2023,'U15','U15',11,last3=True)
U15_system.division.CreateTeams(
    [

"VMW Berlin U15 A",
"VMW Berlin U15 B",
"Powisle U14",
"UKS Kaniow U15",
"Nagymaros U14",
"UKS Katowice U15",
"Dresden U15",
"VK Berlin U15",
"Czech U15W",
"Czech U15M",
"Lesna U14",

        # "Czech U15 M",
        # "Dresden U15-1",
        # "Kwisa Leszna U15",
        # "VMW Berlin U14",
        # "Dresden U15-2",
        # "Katowice U15",
        # "Czech U15 W",
        # "Prague U15",
    ]
)

####################################################
# men 2
Men2_system = TwoGroups(prague2023,'Men 2','Men2',8,semi5_8=True)
Men2_system.division.CreateTeams(
    [
"WCH Berlin",
"KC Kelheim",
"Linz",
"Nagymaros U21",
"Dresden Men",
"KTW 2",
"DobroTeen",

# presunuta U18
"UKS Kaniow U18",
# "Czech U18",

        # "Goettingen B",
        # "KC Kelheim",
        # "SG Potsdam",
        # "Leipzig",
        # "WCH Berlin",
        # "Kwisa Lesna",
        # "VMW Berlin Men",
        # "Jägi Berlin",
        # "DobroPtaah",
        # "KGL Hannover",
        # "Dresden Men",
        # "Schleißheimer PC",
    ]
)

####################################################
# U18

# U18_system = SingleGroupDivisionSystem(prague2023,'U18','U18',7,semi=False,final_for=1)
# U18_system.division.CreateTeams(
#     [
#         "UKK Wien U18",
#         "Kaniow U16",
#         "Kalisz U18",
#         "Kalisz U16",
#         "Czech U18",
#         "Kalisz U16 Girls",
#         "Kwisa Lesna U18",
#
#     ]
# )



####################################################
# U12

U12_system = SingleGroup2Rounds(prague2023,'U12','U12',3,add_referees = False)
U12_system.division.CreateTeams(
    [

"Powisle U12",
"Dresden U12",
"Czech U12",

    ]
)

## naplanujeme zapasy

ts = TournamentScheduler(prague2023,3)

# optimize pitches
# ts.tdo._reduceColumns(ts.pitches)
ts.tdo._reduceColumnsOnePitch(ts.pitches)
# add referees
ts.AddReferees()
# ts.schedule.dropna(inplace=True, how='all')

# optimize games
ts.tdo._reduceEmptySlots01(40)
ts.tdo._reduceEmptySlots02(40)
ts.tdo._reduceEmptySlots03(40)

ts.Schedule(
    [
        (datetime.datetime(2023,5,20,7,00,tzinfo = pytz.utc),datetime.datetime(2023,5,20,19,00,tzinfo = pytz.utc)),
        (datetime.datetime(2023,5,21,7,00,tzinfo = pytz.utc),datetime.datetime(2023,5,21,22,30,tzinfo = pytz.utc)),
        # (datetime.datetime(2022,5,30,7,30),datetime.datetime(2022,5,30,23)),
    ]
)
