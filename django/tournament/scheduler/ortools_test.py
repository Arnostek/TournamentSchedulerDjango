from ortools.sat.python import cp_model
from tournament.scheduler.ortools_build_solver_input import build_solver_input
from tournament.scheduler.ortools_build_model import build_model

def ScheduleFromOrtools(self, times, ortools_result):
    """
    Create schedule from OR-Tools solver result.

    Args:
        times: list of (begin, end) datetime tuples, one per time slot,
               same format as Schedule()
        ortools_result: list of (match, slot_index, pitch_index) tuples
                        where slot_index is an index into `times` and
                        pitch_index is 0-based pitch number
    """
    # validate pitch count
    if len(self.schedule.columns) != self.pitches:
        raise ValueError("Pocet hrist musi byt stejny jako pocet sloupcu schedule!")

    # create pitches
    self.tournament.CreatePitches(self.pitches)

    # create schedule slots for each time entry
    for begin_end in times:
        self.tournament.CreateSchedules(begin_end[0], begin_end[1])

    # get ordered pitches and schedule slots
    pitches = list(self.tournament.pitch_set.all().order_by('id'))

    # place matches into slots based on OR-Tools assignments
    for match, slot_index, pitch_index in ortools_result:
        if not isinstance(match, models.Match):
            continue

        pitch = pitches[pitch_index]
        sch = self.tournament.schedule_set.filter(pitch=pitch)[slot_index]
        sch.match = match
        sch.save()

data = build_solver_input()

slots = list(range(70))      # např. 10 časů
pitches = list(range(5))    # např. 3 hřiště

model_data = build_model(data, slots, pitches)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60
# solver.parameters.log_search_progress = True
result = solver.Solve(model_data["model"])
