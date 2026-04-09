import importlib

from .dataframe_editor import TournamentSchedulerDataframeEditor


def _load_cp_model():
    try:
        return importlib.import_module('ortools.sat.python.cp_model')
    except ImportError:
        return None


class TournamentSchedulerDataframeOptimizerOrtoolsV2:
    """Fresh OR-Tools optimizer skeleton without any constraints."""

    def __init__(self, schedule):
        self.schedule = schedule
        self.DfEditor = TournamentSchedulerDataframeEditor(self.schedule)
        self.DfTester = self.DfEditor.DfTester

    def Optimize(self, desired_slots, dont_move_to_pitch_index=None):
        """Run an empty CP-SAT model and keep schedule unchanged."""
        cp_model = _load_cp_model()
        if cp_model is None:
            raise ImportError('ortools is required for TournamentSchedulerDataframeOptimizerOrtoolsV2')

        if desired_slots <= 0:
            raise ValueError('desired_slots must be positive')

        # Intentionally no variables, constraints, objective, or schedule mutations.
        model = cp_model.CpModel()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 1.0
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError('Empty OR-Tools model did not solve successfully')

        return
