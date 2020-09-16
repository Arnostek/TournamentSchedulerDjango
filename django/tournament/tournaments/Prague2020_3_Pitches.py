from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.TwoGroups import TwoGroups
from tournament.systems.TwoGroups8Teams import TwoGroups8Teams
from tournament.TournamentScheduler import TournamentScheduler

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2020_3_Pitches'

# turnaj
prague2020 = models.Tournament(name = "PIT 2020 Test only!!!!!!", slug = "Test07")
prague2020.save()
print(prague2020)
####################################################
# men
Men_system = SingleGroupDivisionSystem(prague2020,'Men','Men',6)
Men_system.division.CreateTeams(
    [
        # "Kaniow Men",
        # "Tri Stihii",
        "DobroPtaah",
        "Czech U21",
        # "KSC Neckarau",
        "KTW Kalisz Men",
        # "RKV Berlin",
        "Prague C",
        # "Leipzig ?",
        # "SG Havelbruder",
        # "WS Dresden",
        "UKS Katowice",
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
        "Prague Women",
        # "Prague Women 2",
        # "Havelschwester A",
        # "Goettingen Ladies",
        "Poland U21 Women A",
        "Poland U21 Women B",
        # "Leipzig Women",
        # "Havelschwester B",
        "Prague Flowers",
        "United syndrom team",
        "KTW Kalisz/Tanew U16 Girls",
    ]
)

####################################################
# U14

U14_system = SingleGroupDivisionSystem(prague2020,'U14','U14',6)
U14_system.division.CreateTeams(
    [
        "Prague U16",
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
        (datetime.datetime(2020,9,19,8,00),datetime.datetime(2020,9,19,19)),
        (datetime.datetime(2020,9,20,8,00),datetime.datetime(2020,9,20,16))
    ]
)
