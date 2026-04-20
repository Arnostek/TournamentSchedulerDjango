from tournament import models
import datetime
from pathlib import Path

from tournament.systems.SingleGroupDivisionSystem import SingleGroupDivisionSystem
from tournament.systems.TwoGroups8Teams import TwoGroups8Teams
from tournament.systems.TwoGroups import TwoGroups
# from tournament.systems.TwoGroups import TwoGroups
# from tournament.systems.TwoGroups8TeamsCross import TwoGroups8TeamsCross
# from tournament.systems.TwoGroups8TeamsMiddle import TwoGroups8TeamsMiddle
# from tournament.systems.FourGroups12Teams import FourGroups12Teams
# from tournament.systems.FourGroups16Teams import FourGroups16Teams
from tournament.systems.ThreeGroups15Teams import ThreeGroups15Teams
from tournament.systems.FourGroups15Teams import FourGroups15Teams

from tournament.TournamentScheduler import (
    TournamentScheduler
)

import pytz
import yaml

DIVISION_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "prague2026.yaml"

def load_division_configs(config_path=DIVISION_CONFIG_PATH):
    with config_path.open(encoding="utf-8") as config_file:
        division_configs = yaml.safe_load(config_file) or {}

    if not isinstance(division_configs, dict):
        raise ValueError("Division config must be a mapping keyed by division slug.")

    for division_slug, division_config in division_configs.items():
        if not isinstance(division_config, dict):
            raise ValueError(f"Division '{division_slug}' config must be a mapping.")

        if "name" not in division_config:
            raise ValueError(f"Division '{division_slug}' must define 'name'.")

        teams = division_config.get("teams", [])
        if not isinstance(teams, list):
            raise ValueError(f"Division '{division_slug}' teams must be a list.")

        teams_count = division_config.get("teams_count", len(teams))
        if teams_count != len(teams):
            raise ValueError(
                f"Division '{division_slug}' teams_count ({teams_count}) does not match the number of teams ({len(teams)})."
            )

    return division_configs

# run in shell:
# docker compose exec tournament_scheduler python /srv/django/manage.py shell -c 'from tournament.tournaments import Prague2025_Ortools'

# turnaj
tslug = "PIT2026_SEEDING_17"
tname = "PIT 2026 TEST (teams, seeding)"
prague2026 = models.Tournament(name = tname, slug = tslug)
prague2026.save()
print(prague2026)
####################################################
# men 1

Men1_system = ThreeGroups15Teams(prague2026,'Men Elite','MenElite',15)
Men1_system.division.CreateTeams(
    [
        "RKV Berlin",
        "Team Poznań",
        "Kaniow BKT",
        "DRC Neuburg",
        "VK Berlin",
        "KV Nurnberg",
        "Set Kaniow A",
        "KSV Glauchau",
        "Alytus",
        "KP Praha A",
        "KCNW U21",
        "KP Bremen",
        "POL U21",
        "KC Kelheim",
        "Katowice M",
        # "Singapore M",
        # "Dresden A",
    ]
)


####################################################
# Ladies
Ladies_system = TwoGroups(prague2026,'Ladies','Ladies',9, semi5_8=True)
Ladies_system.division.CreateTeams(
     [
        "Kaniow W",
        "KCNW Berlin W",
        "KSVH W",
        "Neuburg W",
        "Czech W",
        "Czech/German",
        "Powisle W",
        "Katowice W",
        "Bremen W",
        # "Kalisz W",
        # "Dresden W",
    ]
)

####################################################
# men 2
Men2_system = TwoGroups8Teams(prague2026,'Men 2','Men2',8)
Men2_system.division.CreateTeams(
    [
        "VMW Berlin Men",
        "Vidra Old Boys",
        "Nagymaros Men",
        # "KTW Kalisz Men",
        "Potsdam Men",
        "UKK Wien mix",
        "Ukraine Men",
        "Lesna Men",
        "DobroPtaah",
        # "Ukraine Men B",
        # "Dresden B",
    ]
)



####################################################
# U18
U18_system = SingleGroupDivisionSystem(prague2026,'U18','U18',7, final_for=2)
U18_system.division.CreateTeams(
    [
        "Alytus U18",
        "Czech U18 A",
        "KCNW U16",
        "Lesna U18",
        "Kalisz U18",
        "Nagymaros U18",
        "Czech U18 B",
        # "Dresden U18",
    ]
)

####################################################
# U14
U14_system = TwoGroups(prague2026,'U14','U14',9, semi5_8=True)
U14_system.division.CreateTeams(
    [
        "KCNW U14",
        "Powisle U14",
        "Glauchau U14",
        # "VK Berlin U14",
        "Neuburg U14",
        "Lesna U14",
        "Praha U14 M",
        "Praha U14 W",
        # "Dresden U14",
        "SG Franken U14",
        "Ukraine U14",
    ]
)

####################################################
# U12
U12_system = SingleGroupDivisionSystem(prague2026,'U12','U12',5)
U12_system.division.CreateTeams(
    [
        "KCNW U12",
        "DFF Veltrusy U12",
        "Praha U12",
        "Nagymarosz U12",
        "Lesna U12",
        # "Dresden U12",
    ]
)


# scheduler
ts = TournamentScheduler(prague2026,5)
# pridame rozhodci
ts.AddReferees()

# naplanujeme zapasy pomoci OR-Tools 
from tournament.scheduler.ortools_scheduler import ortools_scheduler
ts.schedule = ortools_scheduler(prague2026.id, num_slots=38, num_pitches=5, buffer_every_slots=7)

# zalozime zapasy v DB
ts.Schedule(
    [
        (datetime.datetime(2025,5,17,7,30,tzinfo = pytz.utc),datetime.datetime(2025,5,17,19,00,tzinfo = pytz.utc)),
        (datetime.datetime(2025,5,18,7,30,tzinfo = pytz.utc),datetime.datetime(2025,5,18,23,30,tzinfo = pytz.utc)),
    ]
)

