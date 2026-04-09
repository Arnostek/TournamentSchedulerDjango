def build_model(data, slots, pitches):
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()

    M = data["num_matches"]
    matches = range(M)

    S = len(slots)
    P = len(pitches)

    matches_by_team = data["matches_by_team"]
    matches_by_referee = data["matches_by_referee"]
    matches_by_phase = data["matches_by_phase"]
    matches_by_division = data["matches_by_division"]

    matches_data = data["matches"]

    # --------------------------------------------------
    # 1) Proměnné x[m,s,p]
    # --------------------------------------------------
    x = {}
    for m in matches:
        for s in range(S):
            for p in range(P):
                x[m, s, p] = model.NewBoolVar(f"x_{m}_{s}_{p}")

    # --------------------------------------------------
    # 2) Každý zápas právě jednou
    # --------------------------------------------------
    for m in matches:
        model.Add(
            sum(x[m, s, p] for s in range(S) for p in range(P)) == 1
        )

    # --------------------------------------------------
    # 3) Kapacita: max 1 zápas na (slot, pitch)
    # --------------------------------------------------
    for s in range(S):
        for p in range(P):
            model.Add(
                sum(x[m, s, p] for m in matches) <= 1
            )

    # --------------------------------------------------
    # 4) Tým nemůže hrát 2 zápasy ve stejném slotu
    # --------------------------------------------------
    for t, match_ids in matches_by_team.items():
        for s in range(S):
            model.Add(
                sum(
                    x[m, s, p]
                    for m in match_ids
                    for p in range(P)
                ) <= 1
            )

    # --------------------------------------------------
    # 5) Rozhodčí constraint
    # --------------------------------------------------
    for r, match_ids in matches_by_referee.items():
        for s in range(S):
            model.Add(
                sum(
                    x[m, s, p]
                    for m in match_ids
                    for p in range(P)
                ) <= 1
            )

    # --------------------------------------------------
    # 6) slot_of_match (derived proměnná)
    # --------------------------------------------------
    slot_of_match = {}

    for m in matches:
        slot_of_match[m] = model.NewIntVar(0, S - 1, f"slot_{m}")

        model.Add(
            slot_of_match[m] ==
            sum(
                s * x[m, s, p]
                for s in range(S)
                for p in range(P)
            )
        )

    # --------------------------------------------------
    # 7) Phase ordering
    # --------------------------------------------------
    # optimalizace: jen mezi různými phase
    # phases = sorted(matches_by_phase.keys())

    # for i in range(len(phases)):
    #     for j in range(i + 1, len(phases)):
    #         phase_a = phases[i]
    #         phase_b = phases[j]

    #         for m1 in matches_by_phase[phase_a]:
    #             for m2 in matches_by_phase[phase_b]:
    #                 model.Add(slot_of_match[m1] < slot_of_match[m2])

    # for d in data["division_idx"].values():
    #     for i in range(len(matches_by_division[d]) - 1):
    #         m1 = matches_by_division[d][i]
    #         m2 = matches_by_division[d][i + 1]

    #         model.Add(slot_of_match[m1] <= slot_of_match[m2])

    # --------------------------------------------------
    # 8) Pořadí zápasů v rámci divize podle db_id
    # --------------------------------------------------

    for d in data["division_idx"].values():
        for i in range(len(matches_by_division[d]) - 1):
            m1 = matches_by_division[d][i]
            m2 = matches_by_division[d][i + 1]

            model.Add(slot_of_match[m1] <= slot_of_match[m2])


    # --------------------------------------------------
    # 8) (Volitelné) Division constraints
    # --------------------------------------------------
    # TODO: sem můžeš přidat omezení pitch/slot podle division

    # --------------------------------------------------
    # 9) Objective (zatím žádný = hledáme feasible řešení)
    # --------------------------------------------------
    # model.Minimize(...)

    # --------------------------------------------------
    # 10) návrat
    # --------------------------------------------------
    return {
        "model": model,
        "x": x,
        "slot_of_match": slot_of_match,
    }