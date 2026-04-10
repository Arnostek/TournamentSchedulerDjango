from ortools.sat.python import cp_model
from tournament.scheduler.ortools_build_solver_input import build_solver_input
from tournament.scheduler.ortools_build_model import build_model

data = build_solver_input(2)

slots = list(range(50))      # např. 10 časů
pitches = list(range(5))    # např. 3 hřiště

model_data = build_model(data, slots, pitches)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60
# solver.parameters.log_search_progress = True
result = solver.Solve(model_data["model"])
