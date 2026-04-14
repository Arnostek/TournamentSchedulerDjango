from ortools.sat.python import cp_model

from tournament.scheduler.ortools_build_solver_input import build_solver_input
from tournament.scheduler.ortools_build_model import build_slot_model


def solve_matches(tid, num_slots, num_pitches):
    """
    End-to-end solver runner:
    Django → input → model → solve → output
    """

    # =========================================================
    # 1) BUILD INPUT
    # =========================================================
    solver_input = build_solver_input(tid)

    # =========================================================
    # 2) BUILD MODEL
    # =========================================================
    model, slot_vars = build_slot_model(
        solver_input,
        num_slots=num_slots,
        num_pitches=num_pitches,
        pause=1
    )

    # =========================================================
    # 3) SOLVER SETUP
    # =========================================================
    solver = cp_model.CpSolver()

    solver.parameters.max_time_in_seconds = 30
    solver.parameters.num_search_workers = 8
    solver.parameters.log_search_progress = True  # optional debug

    # =========================================================
    # 4) SOLVE
    # =========================================================
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {
            "status": "INFEASIBLE",
            "solution": None
        }

    # =========================================================
    # 5) EXTRACT SOLUTION
    # =========================================================
    matches = solver_input["matches"]

    solution = []

    for i, match in enumerate(matches):
        solution.append({
            "match_id": match["id"],
            "division": match["division"],
            "home": match["home"],
            "away": match["away"],
            "referee": match["referee"],
            "slot": solver.Value(slot_vars[i]),
        })

    # sort by time
    solution.sort(key=lambda x: x["slot"])

    return {
        "status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
        "solution": solution
    }