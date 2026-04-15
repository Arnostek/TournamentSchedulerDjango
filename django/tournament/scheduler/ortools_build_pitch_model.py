from ortools.sat.python import cp_model
from collections import defaultdict


def build_pitch_model(solver_input, slot_solution, num_pitches):
    """
    PHASE 2: Pitch assignment model

    INPUT:
    - solver_input["matches"]
    - solver_input["division_matches"]
    - slot_solution[m] = assigned slot from phase 1

    OUTPUT:
    - CP-SAT model
    - pitch[m] variable
    """

    model = cp_model.CpModel()

    matches = solver_input["matches"]
    num_matches = len(matches)
    division_matches = solver_input["division_matches"]

    # =========================================================
    # 1) VARIABLES
    # =========================================================
    pitch = {}

    for m in range(num_matches):
        pitch[m] = model.NewIntVar(0, num_pitches - 1, f"pitch_{m}")

    # =========================================================
    # 2) CONFLICTS: same slot → all matches must have different pitch
    # =========================================================
    slot_groups = {}

    for m in range(num_matches):
        s = slot_solution[m]
        slot_groups.setdefault(s, []).append(m)

    for ms in slot_groups.values():
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                model.Add(pitch[ms[i]] != pitch[ms[j]])

    # =========================================================
    # 3) BINARY ASSIGNMENT MATRIX
    # =========================================================
    assign = {}

    for m in range(num_matches):
        for p in range(num_pitches):
            assign[m, p] = model.NewBoolVar(f"assign_{m}_{p}")

            model.Add(pitch[m] == p).OnlyEnforceIf(assign[m, p])
            model.Add(pitch[m] != p).OnlyEnforceIf(assign[m, p].Not())

        # exactly one pitch per match
        model.Add(sum(assign[m, p] for p in range(num_pitches)) == 1)

    # =========================================================
    # 4) DIVISION × PITCH USAGE
    # =========================================================
    used = {}

    for div in division_matches:
        for p in range(num_pitches):
            used[div, p] = model.NewBoolVar(f"used_{div}_{p}")

            # OR over matches in division
            model.AddMaxEquality(
                used[div, p],
                [assign[m, p] for m in division_matches[div]]
            )

    # =========================================================
    # 5) OBJECTIVE: minimize pitch fragmentation per division
    # =========================================================
    model.Minimize(
        sum(
            used[div, p]
            for div in division_matches
            for p in range(num_pitches)
        )
    )

    return model, pitch