from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.TwoGroups8Teams import TwoGroups8Teams
from tournament.systems.TwoGroups import TwoGroups
# from tournament.systems.TwoGroups import TwoGroups
# from tournament.systems.TwoGroups8TeamsCross import TwoGroups8TeamsCross
# from tournament.systems.TwoGroups8TeamsMiddle import TwoGroups8TeamsMiddle
# from tournament.systems.FourGroups12Teams import FourGroups12Teams
from tournament.systems.FourGroups16Teams import FourGroups16Teams
from tournament.systems.FourGroups15Teams import FourGroups15Teams

from tournament.TournamentScheduler import TournamentScheduler

import pytz

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2024'

models.Tournament.objects.get(slug='PIT2024_TEST001').delete()

# turnaj
prague2024 = models.Tournament(name = "PIT 2024 TEST", slug = "PIT2024_TEST001")
prague2024.save()
print(prague2024)
####################################################
# men 1

Men1_system = FourGroups15Teams(prague2024,'Men Elite','MenElite',15)
Men1_system.division.CreateTeams(
    [
        "RKV Berlin",
        "Poland Men",
        "Team Poznań",
        "Kaniow Men",
        "KSVH Men",
        "Prague A",
        "WSD SG Sachsen",
        "UKK Wien",
        "Poland U21",
        "Czech U21",
        "Bremen",
        # "Austria U21",
        "Kwisa Lesna",
        "Blue Men (Hungary)",
        "Nagymaros",
        "KTW Kalisz A",
    ]
)


####################################################
# Ladies
Ladies_system = TwoGroups8Teams(prague2024,'Ladies','Ladies',8)
Ladies_system.division.CreateTeams(
    [
        "UKS SET Kaniów Women",
        "KSVH Women",
        "UKS Kanu Katowice",
        "VMW Berlin Women",
        "SG Sachsen",
        "SG Dresden",
        "Czech U21 Women",
        "Czech/German Women",
    ]
)


####################################################
# U15
U15_system = TwoGroups(prague2024,'U15','U15',11)
U15_system.division.CreateTeams(
    [
        "UKS SET Kaniów U15",
        "Kwisa Lesna U15",
        "VMW Berlin U15 A",
        "VMW Berlin U15 B",
        "WSD U15 2",
        "WSD U15 1",
        "Czech U15 A",
        "Czech U15 B",
        "Szeged U15",
        "Nagymaros U15",
        "VK Berlin U15",

    ]
)

####################################################
# men 2
Men2_system = TwoGroups8Teams(prague2024,'Men 2','Men2',8)
Men2_system.division.CreateTeams(
    [
        "SG Cottbus/Glauchau",
        "USV Potsdam",
        "SG Neckarau/Nürnberg",
        "Leipzig",
        "WCH Berlin",
        "KTW Kalisz B",
        "Dobroptah (Czech)",
        "Szeged",
    ]
)

## naplanujeme zapasy

ts = TournamentScheduler(prague2024,4)

# optimize pitches
# ts.tdo._reduceColumns(ts.pitches)
# ts.tdo._reduceColumnsOnePitch(ts.pitches)
# add referees
ts.AddReferees()
# ts.schedule.dropna(inplace=True, how='all')

# optimize games
ts.tdo._reduceEmptySlots01(40)
ts.tdo._reduceEmptySlots02(40)
ts.tdo._reduceEmptySlots03(40)

ts.Schedule(
    [
        (datetime.datetime(2024,5,25,7,00,tzinfo = pytz.utc),datetime.datetime(2024,5,25,19,00,tzinfo = pytz.utc)),
        (datetime.datetime(2024,5,26,7,00,tzinfo = pytz.utc),datetime.datetime(2024,5,26,23,30,tzinfo = pytz.utc)),
    ]
)
