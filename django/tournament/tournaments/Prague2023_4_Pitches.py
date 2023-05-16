from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.SingleGroup2Rounds import SingleGroup2Rounds
from tournament.systems.TwoGroups import TwoGroups
from tournament.systems.TwoGroups8TeamsCross import TwoGroups8TeamsCross
from tournament.systems.TwoGroups8TeamsMiddle import TwoGroups8TeamsMiddle
from tournament.systems.FourGroups12Teams import FourGroups12Teams
from tournament.TournamentScheduler import TournamentScheduler
import pytz

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2020_3_Pitches'

# turnaj
prague2023 = models.Tournament(name = "PIT 2023", slug = "PIT2023")
prague2023.save()
print(prague2023)
####################################################
# men 1
Men1_system = SingleGroupDivisionSystem(prague2023,'Men Elite','MenElite',6,semi=True)
Men1_system.division.CreateTeams(
    [
        "Prague A",
        "UKS Katowice Men",
        # "KTW 1",
        "Prague B",
        "Czech U21",
        # "Trakai",
        "Lesna Men",
        "Austria U21",
    ]
)

####################################################
# Ladies
Ladies_system = TwoGroups8TeamsMiddle(prague2023,'Ladies','Ladies',8)
Ladies_system.division.CreateTeams(
    [
        "VMW Berlin Women",
        "KSVH Berlin Women",
        "UKS Katowice Women",
        "UKS Kaniow Women",
        "Austria Women",
        "Dresden Women",
        "Prague Women",
        "Czech U21 Women",
    ]
)



####################################################
# men 2
Men2_system = SingleGroupDivisionSystem(prague2023,'Men 2','Men2',6)
Men2_system.division.CreateTeams(
    [
        "WCH Berlin",
        # "KC Kelheim",
        "Linz",
        "Nagymaros U21",
        "Dresden Men",
        # "KTW 2",
        "UKS Kaniow U18",
        "DobroTeen",
        # "Czech U18",
    ]
)


####################################################
# U15

U15_system = TwoGroups(prague2023,'U15','U15',11,last3=True)
U15_system.division.CreateTeams(
    [
        "VMW Berlin U15 A",
        "VMW Berlin U15 B",
        "Nagymaros U14",
        "UKS Kaniow U15",
        "Powisle U14",
        "UKS Katowice U15",
        "Dresden U15",
        "VK Berlin U15",
        "Czech U15W",
        "Czech U15M",
        "Lesna U14",

    ]
)

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

ts = TournamentScheduler(prague2023,4)

# optimize pitches
# ts.tdo._reduceColumns(ts.pitches)
ts.tdo._reduceColumnsOnePitch(ts.pitches)
# add referees
ts.AddReferees()
# ts.schedule.dropna(inplace=True, how='all')

# optimize games
ts.tdo._reduceEmptySlots01(31)
ts.tdo._reduceEmptySlots02(31)
ts.tdo._reduceEmptySlots03(31)

ts.Schedule(
    [
        (datetime.datetime(2023,5,20,7,30,tzinfo = pytz.utc),datetime.datetime(2023,5,20,18,00,tzinfo = pytz.utc)),
        (datetime.datetime(2023,5,21,7,30,tzinfo = pytz.utc),datetime.datetime(2023,5,21,15,30,tzinfo = pytz.utc)),
        # (datetime.datetime(2022,5,30,7,30),datetime.datetime(2022,5,30,23)),
    ]
)
