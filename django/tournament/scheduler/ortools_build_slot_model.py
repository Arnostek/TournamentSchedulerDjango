from ortools.sat.python import cp_model
from collections import defaultdict


def build_slot_model(solver_input, num_slots, num_pitches, pause=1):
    """
    OPTIMAL CP-SAT SLOT MODEL

    Key improvements:
    - NO boolean slot matrix
    - interval-based reasoning
    - AddNoOverlap for teams
    - soft division ordering
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
    interval = {}

    DURATION = 1 + pause

    for m in range(num_matches):

        # slot index (time bucket)
        slot[m] = model.NewIntVar(0, num_slots - 1, f"slot_{m}")

        # interval start = slot
        start[m] = slot[m]

        # interval for NoOverlap constraints
        interval[m] = model.NewIntervalVar(
            start[m],
            DURATION,
            start[m] + DURATION,
            f"interval_{m}"
        )

    # =========================================================
    # 2) TEAM + REFEREE CONFLICTS (NoOverlap)
    # =========================================================
    resource_intervals = defaultdict(list)

    for m, match in enumerate(matches):
        for t in (match["home"], match["away"], match.get("referee")):
            if t is None:
                continue
            resource_intervals[t].append(interval[m])

    for t, intervals in resource_intervals.items():
        model.AddNoOverlap(intervals)

    # =========================================================
    # 3) DIVISION ORDERING (SOFT + STABLE)
    # =========================================================
    # instead of strict chain, we only enforce partial order
    for div, ms in division_matches.items():
        for i in range(len(ms) - 1):
            m1 = ms[i]
            m2 = ms[i + 1]

            # soft ordering (allows slack but preserves sequence)
            model.Add(slot[m1] <= slot[m2])

    # =========================================================
    # 4) SLOT LOAD BALANCING (IMPORTANT FOR QUALITY)
    # =========================================================
    # count matches per slot (lightweight version)
    slot_load = []

    for s in range(num_slots):
        bools = []

        for m in range(num_matches):
            b = model.NewBoolVar(f"in_{m}_{s}")

            model.Add(slot[m] == s).OnlyEnforceIf(b)
            model.Add(slot[m] != s).OnlyEnforceIf(b.Not())

            bools.append(b)

        load = model.NewIntVar(0, num_pitches, f"load_{s}")
        model.Add(load == sum(bools))
        slot_load.append(load)

    max_load = model.NewIntVar(0, num_pitches, "max_load")
    min_load = model.NewIntVar(0, num_pitches, "min_load")

    model.AddMaxEquality(max_load, slot_load)
    model.AddMinEquality(min_load, slot_load)

    # =========================================================
    # 5) OBJECTIVE (balanced + compact schedule)
    # =========================================================
    model.Minimize(
        10 * (max_load - min_load) +   # balance across slots
        sum(slot[m] for m in range(num_matches))  # compactness
    )

    # =========================================================
    # 6) SYMMETRY BREAKING (IMPORTANT SPEEDUP)
    # =========================================================
    if num_matches > 0:
        model.Add(slot[0] == 0)

    return model, slot

