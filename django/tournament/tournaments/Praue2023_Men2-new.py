# Hruby postup jak zmenit jednu divizi po rozbehu turnaje

from tournament import models
import datetime
from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.SingleGroup2Rounds import SingleGroup2Rounds

# Starou divizi prejmenujeme, pozdeji i smazeme


# posledni turnaj v DB
prague2023 = Tournament.objects.last()

# nova divize - zvolime tymy a system
Men2_system = SingleGroup2Rounds(prague2023,'Men 2','Men2',4)
Men2_system.division.CreateTeams(
    [
        "WCH Berlin",
        # "KC Kelheim",
        # "Linz",
        "Nagymaros U21",
        "Dresden Men",
        # "KTW 2",
        # "UKS Kaniow U18",
        "DobroTeen",
        # "Czech U18",
    ]
)


# fce na zmenu schedule

def change_match(slot_id,match):

    slot = Schedule.objects.get(id=slot_id)
    slot.match = Match.objects.get(id = match)
    slot.save()

# ve spielplanu si najdeme sloty ze stare divize a match id pro nove zapasy
change_match(s1,m1)
change_match(s2,m2)
change_match(s3,m3)
...

# zbyle matche stare divize smazeme

def del_match(slot_id):
    slot = Schedule.objects.get(id=slot_id)
    slot.match = None
    slot.save()

del_match(m1)
del_match(m2)
del_match(m3)
.....
