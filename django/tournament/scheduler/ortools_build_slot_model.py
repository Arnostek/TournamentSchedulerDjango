from ortools.sat.python import cp_model
from collections import defaultdict


def _reserved_pitch_for_slot(slot_index, num_pitches, buffer_every_slots):
    if not buffer_every_slots or buffer_every_slots <= 0:
        return None

    if (slot_index + 1) % buffer_every_slots != 0:
        return None

    buffer_index = ((slot_index + 1) // buffer_every_slots) - 1
    return buffer_index % num_pitches


def build_slot_model(
    solver_input,
    num_slots,
    num_pitches,
    pause=1,
    phase_change_pause=2,
    buffer_every_slots=None,
):
    """
    OPTIMAL CP-SAT SLOT MODEL

    Key improvements:
    - NO boolean slot matrix
    - interval-based reasoning
    - AddNoOverlap for teams
    - soft division ordering
    - balanced division finish times
    - evenly spread division matches
    - optional rotating buffer slots
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
    # 3) DIVISION ORDERING + PHASE CHANGE GAPS
    # =========================================================
    # Preserve division order and require extra slack after a phase change.
    for div, ms in division_matches.items():
        for i in range(len(ms) - 1):
            m1 = ms[i]
            m2 = ms[i + 1]

            min_gap = 0
            if matches[m1]["phase"] != matches[m2]["phase"]:
                min_gap = phase_change_pause + 1

            model.Add(slot[m2] >= slot[m1] + min_gap)

    # =========================================================
    # 4) DIVISION FINISH BALANCING
    # =========================================================
    division_ends = []
    total_division_start = 0
    total_division_tail = 0
    total_division_profile_deviation = 0
    total_division_gap_imbalance = 0

    for div, ms in division_matches.items():
        division_start = model.NewIntVar(0, num_slots - 1, f"division_start_{div}")
        division_end = model.NewIntVar(0, num_slots - 1, f"division_end_{div}")

        model.AddMinEquality(division_start, [slot[m] for m in ms])
        model.AddMaxEquality(division_end, [slot[m] for m in ms])

        division_span = model.NewIntVar(0, num_slots - 1, f"division_span_{div}")
        model.Add(division_span == division_end - division_start)

        division_tail = model.NewIntVar(0, num_slots - 1, f"division_tail_{div}")
        model.Add(division_tail == (num_slots - 1) - division_end)

        total_division_start += division_start
        total_division_tail += division_tail
        division_ends.append(division_end)

        gap_count = len(ms) - 1

        if gap_count > 0:
            for i, match_index in enumerate(ms):
                profile_delta = model.NewIntVar(
                    -(num_slots - 1) * gap_count,
                    (num_slots - 1) * gap_count,
                    f"division_profile_delta_{div}_{i}"
                )
                model.Add(profile_delta == gap_count * slot[match_index] - i * (num_slots - 1))

                profile_abs = model.NewIntVar(
                    0,
                    (num_slots - 1) * gap_count,
                    f"division_profile_abs_{div}_{i}"
                )
                model.AddAbsEquality(profile_abs, profile_delta)
                total_division_profile_deviation += profile_abs

        if len(ms) > 2:
            gap_terms = []

            for i in range(gap_count):
                gap = model.NewIntVar(0, num_slots - 1, f"division_gap_{div}_{i}")
                model.Add(gap == slot[ms[i + 1]] - slot[ms[i]])

                gap_delta = model.NewIntVar(
                    -(num_slots - 1) * gap_count,
                    (num_slots - 1) * gap_count,
                    f"division_gap_delta_{div}_{i}"
                )
                model.Add(gap_delta == gap_count * gap - division_span)

                gap_abs = model.NewIntVar(0, (num_slots - 1) * gap_count, f"division_gap_abs_{div}_{i}")
                model.AddAbsEquality(gap_abs, gap_delta)
                gap_terms.append(gap_abs)

            total_division_gap_imbalance += sum(gap_terms)

    division_finish_spread = 0
    if division_ends:
        latest_division_end = model.NewIntVar(0, num_slots - 1, "latest_division_end")
        earliest_division_end = model.NewIntVar(0, num_slots - 1, "earliest_division_end")

        model.AddMaxEquality(latest_division_end, division_ends)
        model.AddMinEquality(earliest_division_end, division_ends)

        division_finish_spread = latest_division_end - earliest_division_end

    # =========================================================
    # 5) SLOT LOAD BALANCING (IMPORTANT FOR QUALITY)
    # =========================================================
    # count matches per slot (lightweight version)
    slot_load = []

    for s in range(num_slots):
        bools = []
        reserved_pitch = _reserved_pitch_for_slot(s, num_pitches, buffer_every_slots)
        slot_capacity = num_pitches - 1 if reserved_pitch is not None else num_pitches

        for m in range(num_matches):
            b = model.NewBoolVar(f"in_{m}_{s}")

            model.Add(slot[m] == s).OnlyEnforceIf(b)
            model.Add(slot[m] != s).OnlyEnforceIf(b.Not())

            bools.append(b)

        load = model.NewIntVar(0, slot_capacity, f"load_{s}")
        model.Add(load == sum(bools))
        balanced_load = model.NewIntVar(0, num_pitches, f"balanced_load_{s}")
        model.Add(balanced_load == load + (num_pitches - slot_capacity))
        slot_load.append(balanced_load)

    max_load = model.NewIntVar(0, num_pitches, "max_load")
    min_load = model.NewIntVar(0, num_pitches, "min_load")

    model.AddMaxEquality(max_load, slot_load)
    model.AddMinEquality(min_load, slot_load)

    # =========================================================
    # 6) OBJECTIVE (division spread across full tournament + even spacing + slot balance)
    # =========================================================
    model.Minimize(
        1000 * division_finish_spread +
        300 * total_division_profile_deviation +
        150 * total_division_gap_imbalance +
        75 * total_division_start +
        75 * total_division_tail +
        10 * (max_load - min_load) +   # balance across slots
        sum(slot[m] for m in range(num_matches))  # compactness
    )

    # =========================================================
    # 7) SYMMETRY BREAKING (IMPORTANT SPEEDUP)
    # =========================================================
    if num_matches > 0:
        model.Add(slot[0] == 0)

    return model, slot

