from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.FourGroups13Teams import FourGroups13Teams
from tournament.systems.MinGames import MinGames16Teams,MinGames6Teams
from tournament.TournamentScheduler import TournamentScheduler

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2019_5_Pitches'

# turnaj
prague2019 = models.Tournament(name = "Test 13 tymu", slug = "T13")
prague2019.save()
####################################################
# men A
MenA_system = FourGroups13Teams(prague2019,'Men A','MenA',13)
MenA_system.division.CreateTeams(
    [
        "Gottingen",
        "Warsawa Powisle Men",
        "Kaniow Men",
        "Neuburg Men",
        "Prague A",
        "Prague B",
        "Austria Men",
        "KTW Kalisz",
        "RKV Berlin",
        "Kwisa Lesna Men",
        "9ValA",
        "Vidra A",
        "Polska Men"
    ]
)
## naplanujeme zapasy

ts = TournamentScheduler(prague2019,1)
ts.Schedule(
    [
        (datetime.datetime(2019,5,25,7),datetime.datetime(2019,5,25,19)),
        (datetime.datetime(2019,5,26,7),datetime.datetime(2019,5,26,17))
    ]
)
