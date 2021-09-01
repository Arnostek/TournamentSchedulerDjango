from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.SingleGroup5teams import SingleGroup5teams
from tournament.systems.TwoGroups8Teams import TwoGroups8Teams
from tournament.TournamentScheduler import TournamentScheduler

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2020_3_Pitches'

# turnaj
prague2021 = models.Tournament(name = "PIT 2021", slug = "PIT2021")
prague2021.save()
print(prague2021)
####################################################
# men 1
Men1_system = TwoGroups8Teams(prague2021,'Men 1','Men1',8)
Men1_system.division.CreateTeams(
    [
        "Kwisa Lesna",
        # "Kaniow Men",
        "RKV Berlin",
        "Czech Men Emerites",
        "U21 Czech Men",
        # "Glauchau A",
        "Katowice Men",
        "Nagymaros Men",
        "AVSK",
        "Austria",
    ]
)

####################################################
# Ladies
Ladies_system = SingleGroupDivisionSystem(prague2021,'Ladies','Ladies',6,semi=True)
Ladies_system.division.CreateTeams(
    [
#        "Coburg",
        "MuRaHa",
        "Swiss ladies",
        "Czech Women A",
        "Havelschwester",
        "Nagymaros Women",
        "Czech Women B",
    ]
)

####################################################
# Juniors

Juniors_system = TwoGroups8Teams(prague2021,'Juniors','Juniors',8)
Juniors_system.division.CreateTeams(
    [
        "Poland U16",
        "Szeged U16",
        "Nagymaros U18 B",
        "Czech U16",
        "Kaniow U16",
        # "Glauchau U14"
        "Katowice U14",
        "Czech U14 A",
        "Czech U14 B",
    ]
)

####################################################
# men 2
Men2_system = SingleGroup5teams(prague2021,'Men 2','Men2',5)
Men2_system.division.CreateTeams(
    [
        "Dresden Men",
        "Nürnberg-Neckarau",
        "Czech Men Dobroptah",
        # "Glauchau B",
        "Munich mix team",
        "Nagymaros U18 B",
    ]
)
## naplanujeme zapasy

ts = TournamentScheduler(prague2021,3)
ts.Optimize(40)

ts.Schedule(
    [
        (datetime.datetime(2021,9,4,7,30),datetime.datetime(2021,9,4,18,30)),
        (datetime.datetime(2021,9,5,7,30),datetime.datetime(2021,9,5,23))
    ]
)
