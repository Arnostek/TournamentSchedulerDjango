from tournament import models
import datetime

from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.TwoGroups8Teams import TwoGroups8Teams
from tournament.systems.TwoGroups import TwoGroups
# from tournament.systems.TwoGroups import TwoGroups
from tournament.systems.TwoGroups8TeamsCross import TwoGroups8TeamsCross
# from tournament.systems.TwoGroups8TeamsMiddle import TwoGroups8TeamsMiddle
# from tournament.systems.FourGroups12Teams import FourGroups12Teams
from tournament.systems.FourGroups16Teams import FourGroups16Teams
from tournament.systems.ThreeGroups15Teams import ThreeGroups15Teams
from tournament.systems.FourGroups15Teams import FourGroups15Teams
from tournament.systems.ThreeGroups9Teams import ThreeGroups9Teams

from tournament.TournamentScheduler import (
    TournamentScheduler
)
from .load_division_configs import load_division_configs

import pytz

# run in shell:
# docker compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2025_Ortools'

# turnaj
divisions = load_division_configs("config/prague2026.yaml")

tslug = "PIT2026_TEST_48"
tname = "PIT 2026 TEST (U12 last 3)"
prague2026 = models.Tournament(name = tname, slug = tslug)
prague2026.save()
print(prague2026)

# map division_id -> list of preferred pitch indices (0-based, ordered by preference)
preferred_pitches = {}

# men 1
division_slug = 'MenElite'
division_config = divisions[division_slug]
Men1_system = ThreeGroups15Teams(prague2026,division_config['name'],division_slug,len(division_config['teams']))
Men1_system.division.CreateTeams(division_config['teams'])
preferred_pitches[Men1_system.division.id] = [0, 1, 2, 3, ]

# Ladies
division_slug = 'Ladies'
division_config = divisions[division_slug]
Ladies_system = ThreeGroups9Teams(prague2026,division_config['name'],division_slug,len(division_config['teams']))
Ladies_system.division.CreateTeams(division_config['teams'])
preferred_pitches[Ladies_system.division.id] = [1, 0, 2, 3, 4]

# men 2
division_slug = 'Men2'
division_config = divisions[division_slug]
Men2_system = SingleGroupDivisionSystem(prague2026,division_config['name'],division_slug,len(division_config['teams']), final_for=2)
Men2_system.division.CreateTeams(division_config['teams'])
preferred_pitches[Men2_system.division.id] = [3, 2, 1, 0, 4]

# U18
division_slug = 'U18'
division_config = divisions[division_slug]
U18_system = SingleGroupDivisionSystem(prague2026,division_config['name'],division_slug,len(division_config['teams']), final_for=2)
U18_system.division.CreateTeams(division_config['teams'])
preferred_pitches[U18_system.division.id] = [1, 0, 2, 3, ]

# U14
division_slug = 'U14'
division_config = divisions[division_slug]
U14_system = TwoGroups8TeamsCross(prague2026,division_config['name'],division_slug,len(division_config['teams']))
U14_system.division.CreateTeams(division_config['teams'])
preferred_pitches[U14_system.division.id] = [4, 3, 2, 1, 0]

# U12
division_slug = 'U12'
division_config = divisions[division_slug]
U12_system = SingleGroupDivisionSystem(prague2026,division_config['name'],division_slug,len(division_config['teams']),last3=True)
U12_system.division.CreateTeams(division_config['teams'])
preferred_pitches[U12_system.division.id] = [4, ]

# scheduler
ts = TournamentScheduler(prague2026,5)
# pridame rozhodci
ts.AddReferees()

# naplanujeme zapasy pomoci OR-Tools 
from tournament.scheduler.ortools_scheduler import ortools_scheduler
ts.schedule = ortools_scheduler(prague2026.id, num_slots=38, num_pitches=5, buffer_every_slots=7, preferred_pitches=preferred_pitches)

# zalozime zapasy v DB
ts.Schedule(
    [
        (datetime.datetime(2025,5,17,7,30,tzinfo = pytz.utc),datetime.datetime(2025,5,17,19,00,tzinfo = pytz.utc)),
        (datetime.datetime(2025,5,18,7,30,tzinfo = pytz.utc),datetime.datetime(2025,5,18,23,30,tzinfo = pytz.utc)),
    ]
)

