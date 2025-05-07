from tournament import models
import datetime
# from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
# from tournament.systems.TwoGroups8Teams import TwoGroups8Teams
from tournament.systems.TwoGroups import TwoGroups
# from tournament.systems.TwoGroups import TwoGroups
# from tournament.systems.TwoGroups8TeamsCross import TwoGroups8TeamsCross
# from tournament.systems.TwoGroups8TeamsMiddle import TwoGroups8TeamsMiddle
# from tournament.systems.FourGroups12Teams import FourGroups12Teams
# from tournament.systems.FourGroups16Teams import FourGroups16Teams
# from tournament.systems.ThreeGroups15Teams import ThreeGroups15Teams
from tournament.systems.FourGroups15Teams import FourGroups15Teams


from tournament.TournamentScheduler import TournamentScheduler

import pytz

# run in shell:
# docker compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2025'

# turnaj
tslug = "PIT2025_TEST23"
prague2025 = models.Tournament(name = tslug, slug = tslug)
prague2025.save()
print(prague2025)
####################################################
# men 1

Men1_system = FourGroups15Teams(prague2025,'Men Elite','MenElite',15)
Men1_system.division.CreateTeams(
    [
        "RKV Berlin", 
        "Kaniow Men A", 
        "Poznań", 
        "KSV Glauchau", 
        "Kaniow Men B", 
        "KV Nürnberg", 
        "DRC Neuburg", 
        "VMW Berlin Men",  
        "Prague A", 
        "UKK Wien", 
        "VK Berlin U21", 
        "Bremen", 
        "Katowice Men", 
        "Nagymaros", 
        "Dresden Men A", 
    ]
)


####################################################
# Ladies
Ladies_system = TwoGroups(prague2025,'Ladies','Ladies',10, semi5_8=True)
Ladies_system.division.CreateTeams(
     [
        "VMW Berlin Women", 
        "Kaniow Women", 
        "MOSW Choszczno Women", 
        "Katowice Women", 
        "Prague Women", 
        "Swiss U21", 
        "Havelbrüder Women", 
        "Girls 99", 
        "Dresden Women", 
        "Prague Girls", 
    ]
)

####################################################
# men 2
Men2_system = TwoGroups(prague2025,'Men 2','Men2',9)
Men2_system.division.CreateTeams(
    [
        "WCH Berlin", 
        "USV Potsdam", 
        "KWS Ukraine Men A", 
        #"KWS Ukraine Men B", 
        "Leśná Men", 
        "Dresden Men B", 
        "DobroPtaah", 
        "Kaniow Men C", 
        "Czech U21 M", 
        #"Innsbruck", 
        "Vidra Old Boys", 
    ]
)

####################################################
# U15
U15_system = TwoGroups(prague2025,'U15','U15',11, semi5_8=True)
U15_system.division.CreateTeams(
    [
        "Kaniow U15", 
        "Wien U15", 
        "Leśná U15", 
        "Dresden U15", 
        "Prague U15", 
        "Havelbrüder U15", 
        "VK Berlin U15", 
        "Alytus U15", 
        "VMW Berlin U15 A", 
        "VMW Berlin U15 B", 
        "Hungary U15", 
    ]
)

####################################################
# U12
U12_system = TwoGroups(prague2025,'U12','U12',8, semi5_8=True)
U12_system.division.CreateTeams(
    [
        "Prague U12", 
        "Dresden U12", 
        "Leśná U12", 
        "Veltrusy U12", 
        "Glauchau U12", 
        "Havelbrüder U12", 
        "Warszawa U12", 
        "Hungary U12", 
    ]
)

## naplanujeme zapasy

ts = TournamentScheduler(prague2025,5)

# optimize pitches
# ts.tdo._reduceColumns(ts.pitches)
# ts.tdo._reduceColumnsOnePitch(ts.pitches)
# add referees
ts.AddReferees()
# ts.schedule.dropna(inplace=True, how='all')



# optimize games
ts.tdo._reduceEmptySlots01(41)
ts.tdo._reduceEmptySlots02(41)
ts.tdo._reduceEmptySlots03(41)

ts.Schedule(
    [
        (datetime.datetime(2025,5,17,7,00,tzinfo = pytz.utc),datetime.datetime(2025,5,17,19,00,tzinfo = pytz.utc)),
        (datetime.datetime(2025,5,18,7,00,tzinfo = pytz.utc),datetime.datetime(2025,5,18,23,30,tzinfo = pytz.utc)),
    ]
)
