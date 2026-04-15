from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
# from tournament.systems.TwoGroups8Teams import TwoGroups8Teams
from tournament.systems.TwoGroups import TwoGroups
# from tournament.systems.TwoGroups import TwoGroups
# from tournament.systems.TwoGroups8TeamsCross import TwoGroups8TeamsCross
# from tournament.systems.TwoGroups8TeamsMiddle import TwoGroups8TeamsMiddle
# from tournament.systems.FourGroups12Teams import FourGroups12Teams
# from tournament.systems.FourGroups16Teams import FourGroups16Teams
from tournament.systems.ThreeGroups15Teams import ThreeGroups15Teams
#from tournament.systems.FourGroups15Teams import FourGroups15Teams

from tournament.TournamentScheduler import (
    TournamentScheduler
)

import pytz

# run in shell:
# docker compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2025_Ortools'

# turnaj
tslug = "PIT2026_TEST_ORTOOLS_02"
tname = "PIT 2026 TEST (OR-Tools)"
prague2026 = models.Tournament(name = tname, slug = tslug)
prague2026.save()
print(prague2026)
####################################################
# men 1

Men1_system = ThreeGroups15Teams(prague2026,'Men Elite','MenElite',15)
Men1_system.division.CreateTeams(
    [
        "Kaniow A",
        "Poznań",
        "KC Kelheim",
        "KP Bremen",
        "DRC Neuburg",
        "KSV Glauchau",
        "RKV Berlin",
        "VK Berlin",
        "Alytus",
        "Kaniow BKT",
        "KV Nurnberg",
        "KP Praha A",
        "KCNW U21",
        "Katowice M",
        # "Singapore M",
        # "Dresden A",
        "POL U21",
    ]
)


####################################################
# Ladies
Ladies_system = TwoGroups(prague2026,'Ladies','Ladies',9, semi5_8=True)
Ladies_system.division.CreateTeams(
     [
        "Kaniow W",
        "Neuburg W",
        # "Kalisz W",
        "Bremen W",
        "Czech/German",
        "Czech W",
        "KSVH W",
        "Powisle W",
        "KCNW Berlin W",
        "Katowice W",
        # "Dresden W",
    ]
)

####################################################
# men 2
Men2_system = TwoGroups(prague2026,'Men 2','Men2',8, semi5_8=True)
Men2_system.division.CreateTeams(
    [
        "Potsdam Men",
        "Nagymaros Men",
        "VMW Berlin Men",
        # "KTW Kalisz Men",
        "Lesna Men",
        "Ukraine Men",
        "Vidra Old Boys",
        "UKK Wien mix",
        "Dobroptaah",
        # "Dresden B",
        # "Ukraine Men B",
    ]
)



####################################################
# U18
U18_system = TwoGroups(prague2026,'U18','U18',7, semi5_8=False)
U18_system.division.CreateTeams(
    [
        "Nagymaros U18",
        "Alytus U18",
        "Kalisz U18",
        "Lesna U18",
        "Czech U18 A",
        "Czech U18 B",
        "KCNW U16",
        # "Dresden U18",
    ]
)

####################################################
# U14
U14_system = TwoGroups(prague2026,'U14','U14',9, semi5_8=True)
U14_system.division.CreateTeams(
    [
        "Neuburg U14",
        "Lesna U14",
        "Ukraine U14",
        "Glauchau U14",
        # "VK Berlin U14",
        "Praha U14 M",
        "Praha U14 W",
        "Powisle U14",
        "KCNW U14",
        # "Dresden U14",
        "SG Franken U14",
    ]
)

####################################################
# U12
U12_system = SingleGroupDivisionSystem(prague2026,'U12','U12',5)
U12_system.division.CreateTeams(
    [
        "Nagymarosz U12",
        "Lesna U12",
        "DFF Veltrusy U12",
        "Praha U12",
        "KCNW U12",
        # "Dresden U12",
    ]
)


# scheduler
ts = TournamentScheduler(prague2026,5)
# pridame rozhodci
ts.AddReferees()

# naplanujeme zapasy pomoci OR-Tools 
from tournament.scheduler.ortools_scheduler import ortools_scheduler
ts.schedule = ortools_scheduler(prague2026.id, num_slots=40, num_pitches=5, buffer_every_slots=7)

# zalozime zapasy v DB
ts.Schedule(
    [
        (datetime.datetime(2025,5,17,7,30,tzinfo = pytz.utc),datetime.datetime(2025,5,17,19,00,tzinfo = pytz.utc)),
        (datetime.datetime(2025,5,18,7,30,tzinfo = pytz.utc),datetime.datetime(2025,5,18,23,30,tzinfo = pytz.utc)),
    ]
)

