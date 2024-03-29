from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.SingleGroup5teams import SingleGroup5teams
from tournament.TournamentScheduler import TournamentScheduler

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2020_3_Pitches'

# turnaj
prague2020 = models.Tournament(name = "PIT 2020", slug = "PIT2020")
prague2020.save()
print(prague2020)
####################################################
# men
Men_system = SingleGroupDivisionSystem(prague2020,'Men','Men',7)
Men_system.division.CreateTeams(
    [
        "Kaniow",
        # "Tri Stihii",
        "UKS Katowice",
        "Czech U21",
        # "KSC Neckarau",
        # "RKV Berlin",
        "DobroPtaah",
        "Prague C",
        "KTW Kalisz Men",
        # "Leipzig ?",
        # "SG Havelbruder",
        # "WS Dresden",
        # "Glauchau",
        "Tanew Księżpol U16",
    ]
)

####################################################
# Ladies
Ladies_system = SingleGroupDivisionSystem(prague2020,'Ladies','Ladies',6)
Ladies_system.division.CreateTeams(
    [
        # "Kaniow Women",
        # "Swiss Ladies ?",
        "Prague Women 1",
        # "Prague Women 2",
        # "Havelschwester A",
        # "Goettingen Ladies",
        "Poland U21 Women A",
        "Poland U21 Women B",
        # "Leipzig Women",
        # "Havelschwester B",
        "Prague Women 2",
        # "United syndrom team",
        "KTW Kalisz/Tanew U16 Girls",
        "Prague U16",
    ]
)

####################################################
# U14

U14_system = SingleGroup5teams(prague2020,'U14','U14',5)
U14_system.division.CreateTeams(
    [
        # "Kaniow U14",
        "Prague U14",
        "KTW Kalisz U14 Boys",
        "KTW Kalisz U14 Girls",
        "Jabko U14",
        # "WS Dresden U14",
        "UKS Katowice U14",
        # "Glauchau U14",
    ]
)
## naplanujeme zapasy

ts = TournamentScheduler(prague2020,2)
# ts.Optimize(40)
ts.Schedule(
    [
        (datetime.datetime(2020,9,19,8,00),datetime.datetime(2020,9,19,18,30)),
        (datetime.datetime(2020,9,20,7,30),datetime.datetime(2020,9,20,18))
    ]
)
