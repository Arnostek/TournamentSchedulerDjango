from ortools.sat.python import cp_model

from tournament.scheduler.ortools_build_solver_input import build_solver_input
from django.tournament.scheduler.ortools_build_slot_model import build_slot_model
from django.tournament.scheduler.ortools_build_pitch_model import build_pitch_model


def run_full_test(tid, num_slots=40, num_pitches=5):
    """
    FULL PIPELINE TEST:
    Django → Slot model → Solve → Pitch model → Solve → Output
    """

    # =========================================================
    # 1) INPUT
    # =========================================================
    solver_input = build_solver_input(tid)

    print("Matches:", solver_input["num_matches"])
    print("Divisions:", len(solver_input["division_matches"]))

    # =========================================================
    # 2) SLOT MODEL (PHASE 1)
    # =========================================================
    slot_model, slot_vars = build_slot_model(
        solver_input,
        num_slots=num_slots,
        num_pitches=num_pitches
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    solver.parameters.num_search_workers = 8

    status = solver.Solve(slot_model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("❌ SLOT MODEL INFEASIBLE")
        return None

    # extract slot solution
    slot_solution = {
        i: solver.Value(slot_vars[i])
        for i in range(solver_input["num_matches"])
    }

    print("✔ Slot model solved")

    # =========================================================
    # 3) PITCH MODEL (PHASE 2)
    # =========================================================
    pitch_model, pitch_vars = build_pitch_model(
        solver_input,
        slot_solution,
        num_pitches=num_pitches
    )

    solver2 = cp_model.CpSolver()
    solver2.parameters.max_time_in_seconds = 30
    solver2.parameters.num_search_workers = 8

    status2 = solver2.Solve(pitch_model)

    if status2 not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("❌ PITCH MODEL INFEASIBLE")
        return None

    print("✔ Pitch model solved")

    # =========================================================
    # 4) BUILD FINAL OUTPUT
    # =========================================================
    matches = solver_input["matches"]

    result = []

    for i, m in enumerate(matches):
        result.append({
            "match_id": m["id"],
            "division": m["division"],
            "home": m["home"],
            "away": m["away"],
            "referee": m["referee"],
            "slot": slot_solution[i],
            "pitch": solver2.Value(pitch_vars[i]),
        })

    result.sort(key=lambda x: (x["slot"], x["pitch"]))

    return result