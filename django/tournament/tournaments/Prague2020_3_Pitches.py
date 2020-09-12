from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.TwoGroups import TwoGroups
from tournament.TournamentScheduler import TournamentScheduler

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import prague2020_5_Pitches'

# turnaj
prague2020 = models.Tournament(name = "PIT 2020", slug = "PIT2020")
prague2020.save()
print(prague2020)
####################################################
# men
Men_system = TwoGroups(prague2020,'Men','Men',11)
Men_system.division.CreateTeams(
    [
        "Kaniow Men",
        # "Tri Stihii",
        "Prague B",
        "Czech U21",
        # "KSC Neckarau",
        "KTW Kalisz Men",
        "RKV Berlin",
        "Prague C",
        "Leipzig ?",
        "SG Havelbruder",
        "WS Dresden",
        "UKS Katowice",
        "Glauchau",
    ]
)

####################################################
# Ladies
Ladies_system = TwoGroups(prague2020,'Ladies','Ladies',9)
Ladies_system.division.CreateTeams(
    [
        "Kaniow Women",
        "Swiss Ladies ?",
        "Prague Women",
        # "Prague Women 2",
        "Havelschwester A",
        # "Goettingen Ladies",
        "Poland U21 Women A",
        "Poland U21 Women B",
        # "Leipzig Women",
        "Havelschwester B",
        "Prague Flowers",
        "United syndrom team",
    ]
)

####################################################
# U16
u16_system = SingleGroupDivisionSystem(prague2020,'U16','U16',5)
u16_system.division.CreateTeams(
    [
        "Prague U16",
        "Tanew Księżpol U16",
        "KTW Kalisz U16 Boys",
        "KTW Kalisz/Tanew U16 Girls",
        # "Kanu team Berlin U16",
        "WS Dresden U16",
    ]
)

####################################################
# U14

U14_system = TwoGroups(prague2020,'U14','U14',8)
U14_system.division.CreateTeams(
    [
        "Kaniow U14",
        "Prague U14",
        "KTW Kalisz U14 Boys",
        "KTW Kalisz U14 Girls",
        "Jabko U14",
        "WS Dresden U14",
        "UKS Katowice U14",
        "Glauchau U14",
    ]
)
## naplanujeme zapasy

ts = TournamentScheduler(prague2020,3)
ts.Optimize(40)
ts.Schedule(
    [
        (datetime.datetime(2020,9,19,7,00),datetime.datetime(2020,9,19,19)),
        (datetime.datetime(2020,9,20,7,00),datetime.datetime(2020,9,20,16))
    ]
)
