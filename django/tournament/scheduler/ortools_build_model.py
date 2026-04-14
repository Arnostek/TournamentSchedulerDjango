from ortools.sat.python import cp_model
from collections import defaultdict


def build_slot_model(solver_input, num_slots, num_pitches, pause=1):
    """
    Phase 1: SLOT SCHEDULING ONLY (no pitches)

    solver_input:
        {
            "matches": [...],
            "num_matches": int,
            "division_matches": {div: [match_idx,...]},
        }
    """

    model = cp_model.CpModel()

    matches = solver_input["matches"]
    num_matches = solver_input["num_matches"]
    division_matches = solver_input["division_matches"]

    # =========================================================
    # 1) VARIABLES
    # =========================================================
    slot = {}
    start = {}
    end = {}
    interval = {}

    for m in range(num_matches):
        slot[m] = model.NewIntVar(0, num_slots - 1, f"slot_{m}")

        start[m] = slot[m]

        end[m] = model.NewIntVar(0, num_slots + 10, f"end_{m}")

        model.Add(end[m] == start[m] + 1 + pause)

        interval[m] = model.NewIntervalVar(
            start[m],
            1 + pause,
            end[m],
            f"interval_{m}"
        )

    # =========================================================
    # 2) TEAM / REFEREE CONSTRAINTS (NO OVERLAP)
    # =========================================================
    team_intervals = defaultdict(list)

    for m, match in enumerate(matches):
        for team in [match["home"], match["away"], match.get("referee")]:
            if team is None:
                continue
            team_intervals[team].append(interval[m])

    for team, ints in team_intervals.items():
        model.AddNoOverlap(ints)

    # =========================================================
    # 3) DIVISION ORDERING
    # =========================================================
    for div, ms in division_matches.items():
        for i in range(len(ms) - 1):
            m1 = ms[i]
            m2 = ms[i + 1]

            model.Add(slot[m1] < slot[m2])

    # =========================================================
    # 4) SLOT CAPACITY (<= pitches - 1 buffer)
    # =========================================================
    for s in range(num_slots):
        in_slot = []

        for m in range(num_matches):
            b = model.NewBoolVar(f"in_{m}_{s}")

            model.Add(slot[m] == s).OnlyEnforceIf(b)
            model.Add(slot[m] != s).OnlyEnforceIf(b.Not())

            in_slot.append(b)

        model.Add(sum(in_slot) <= num_pitches - 1)

    # =========================================================
    # 5) OBJECTIVE (simple but stable)
    # =========================================================
    model.Minimize(
        sum(slot[m] for m in range(num_matches))
    )

    # =========================================================
    # 6) SYMMETRY BREAKING
    # =========================================================
    if num_matches > 0:
        model.Add(slot[0] == 0)

    return model, slot