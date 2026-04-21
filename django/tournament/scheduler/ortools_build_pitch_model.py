from ortools.sat.python import cp_model


def _preferred_empty_pitch(slot_index, num_pitches):
    return slot_index % num_pitches


def _get_preferred_pitch_order(preferred_pitches, division_id, num_pitches):
    if not preferred_pitches:
        return list(range(num_pitches))

    if division_id in preferred_pitches:
        ordered_pitches = preferred_pitches[division_id]
    elif str(division_id) in preferred_pitches:
        ordered_pitches = preferred_pitches[str(division_id)]
    else:
        return list(range(num_pitches))

    if not isinstance(ordered_pitches, list) or len(ordered_pitches) == 0:
        raise ValueError(f"Preferred pitches for division '{division_id}' must be a non-empty list.")

    if len(set(ordered_pitches)) != len(ordered_pitches):
        raise ValueError(f"Preferred pitches for division '{division_id}' contain duplicates.")

    for pitch_index in ordered_pitches:
        if not isinstance(pitch_index, int) or pitch_index < 0 or pitch_index >= num_pitches:
            raise ValueError(
                f"Preferred pitch '{pitch_index}' for division '{division_id}' must be an integer in range 0..{num_pitches - 1}."
            )

    return ordered_pitches


def build_pitch_model(solver_input, slot_solution, num_pitches, preferred_pitches=None):
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
    preference_penalty = 0
    division_pitch_preferences = {
        div: _get_preferred_pitch_order(preferred_pitches, div, num_pitches)
        for div in division_matches
    }

    for m in range(num_matches):
        division_id = matches[m]["division"]
        preferred_order = division_pitch_preferences[division_id]
        allowed_pitch_set = set(preferred_order)
        preferred_rank = {pitch_index: rank for rank, pitch_index in enumerate(preferred_order)}

        for p in range(num_pitches):
            assign[m, p] = model.NewBoolVar(f"assign_{m}_{p}")

            model.Add(pitch[m] == p).OnlyEnforceIf(assign[m, p])
            model.Add(pitch[m] != p).OnlyEnforceIf(assign[m, p].Not())

            if p not in allowed_pitch_set:
                model.Add(assign[m, p] == 0)
            else:
                preference_penalty += preferred_rank[p] * assign[m, p]

        # exactly one pitch per match
        model.Add(sum(assign[m, p] for p in range(num_pitches)) == 1)

    # =========================================================
    # 4) ROTATING EMPTY PITCH ON NON-FULL SLOTS
    # =========================================================
    for s, ms in slot_groups.items():
        if len(ms) >= num_pitches:
            continue

        reserved_pitch = _preferred_empty_pitch(s, num_pitches)

        for m in ms:
            model.Add(assign[m, reserved_pitch] == 0)

    # =========================================================
    # 5) DIVISION × PITCH USAGE
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
    # 6) OBJECTIVE: minimize pitch fragmentation per division
    # =========================================================
    fragmentation_penalty = sum(
            used[div, p]
            for div in division_matches
            for p in range(num_pitches)
        )

    model.Minimize(1000 * fragmentation_penalty + preference_penalty)

    return model, pitch