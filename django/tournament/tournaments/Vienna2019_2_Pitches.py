from tournament import models
import datetime
from tournament.systems.FourGroups12Teams import FourGroups12Teams
from tournament.systems.SingleGroup2Rounds import SingleGroup2Rounds

from tournament.TournamentScheduler import TournamentScheduler

# run in shell:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Vienna2019_2_Pitches'

# turnaj
vienna2019 = models.Tournament(name = "Vienna 2019", slug = "VIE2019")
vienna2019.save()
print(vienna2019)
####################################################
# Div I
MenA_system = FourGroups12Teams(vienna2019,'Division I','Div1',12)
MenA_system.division.CreateTeams(
    [
        "Nagymaros",
        "KGW Essen",
        "Team AUT",
        "KP Prag A",
        "Vidra A",
        "Vidra B",
        "KP Prag B",
        "Schnecke Linz",
        "UKK Wien",
        "UKK Wien Ladies",
        "Nagymaros Ladies",
        "Nagymaros U16",
    ]
)

####################################################
# U16
u16_system = SingleGroup2Rounds(vienna2019,'U16','U16',4)
u16_system.division.CreateTeams(
    [
        "Szeged U16",
        "Nagymaros U16",
        "KP Prague U16",
        "UKK Wien U16",
        #"Kalisz U16",
    ]
)

## naplanujeme zapasy

ts = TournamentScheduler(vienna2019,pitches = 2)
ts._reduceEmptySlots(35)
ts.Schedule(
    [
        (datetime.datetime(2019,8,6,8,30),datetime.datetime(2019,8,6,19)),
        (datetime.datetime(2019,8,7,8,30),datetime.datetime(2019,8,7,19))
    ]
)
