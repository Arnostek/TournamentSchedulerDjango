import importlib

from .. import models
from .dataframe_editor import TournamentSchedulerDataframeEditor


def _load_cp_model():
    try:
        return importlib.import_module('ortools.sat.python.cp_model')
    except ImportError:
        return None


class TournamentSchedulerDataframeOptimizerOrtools:
    """CP-SAT optimizer for schedule dataframe using OR-Tools."""

    def __init__(self, schedule):
        self.schedule = schedule
        self.DfEditor = TournamentSchedulerDataframeEditor(self.schedule)
        self.DfTester = self.DfEditor.DfTester

    def _collect_matches(self):
        matches = []
        for row_ind in range(len(self.schedule)):
            for pitch_ind in self.schedule.columns:
                cell = self.schedule.iloc[row_ind, pitch_ind]
                if isinstance(cell, models.Match):
                    matches.append(
                        {
                            'match': cell,
                            'orig_row': row_ind,
                            'orig_pitch': int(pitch_ind),
                            'teams': [tph for tph in [cell.home, cell.away, cell.referee] if tph is not None],
                        }
                    )
        return matches

    def _team_key(self, tph):
        # Stable key for model grouping. Prefer DB pk when available.
        pk = getattr(tph, 'pk', None)
        if pk is not None:
            return ('pk', int(pk))
        return ('obj', id(tph))

    def _build_and_solve(self, matches, target_rows, pitch_indexes):
        cp_model = _load_cp_model()
        if cp_model is None:
            return None

        model = cp_model.CpModel()
        num_matches = len(matches)
        num_pitches = len(pitch_indexes)

        x = {}
        for i in range(num_matches):
            for r in range(target_rows):
                for p in range(num_pitches):
                    x[(i, r, p)] = model.NewBoolVar(f'x_{i}_{r}_{p}')

        # Each match exactly once.
        for i in range(num_matches):
            model.Add(sum(x[(i, r, p)] for r in range(target_rows) for p in range(num_pitches)) == 1)

        # One match per slot.
        for r in range(target_rows):
            for p in range(num_pitches):
                model.Add(sum(x[(i, r, p)] for i in range(num_matches)) <= 1)

        # Helper row vars for ordering and objective.
        row_vars = {}
        for i in range(num_matches):
            row_var = model.NewIntVar(0, target_rows - 1, f'row_{i}')
            model.Add(row_var == sum(r * x[(i, r, p)] for r in range(target_rows) for p in range(num_pitches)))
            row_vars[i] = row_var

        # Preserve per-original-pitch match order.
        by_pitch = {}
        for i, item in enumerate(matches):
            by_pitch.setdefault(item['orig_pitch'], []).append((item['orig_row'], i))
        for pitch, ordered in by_pitch.items():
            ordered.sort(key=lambda it: it[0])
            for idx in range(len(ordered) - 1):
                i1 = ordered[idx][1]
                i2 = ordered[idx + 1][1]
                model.Add(row_vars[i1] <= row_vars[i2])

        # Team cannot play/ref adjacent (same row or +-1 row).
        team_to_matches = {}
        for i, item in enumerate(matches):
            for tph in item['teams']:
                team_to_matches.setdefault(self._team_key(tph), []).append(i)

        for team_matches in team_to_matches.values():
            if len(team_matches) <= 1:
                continue
            for pos_a in range(len(team_matches) - 1):
                i = team_matches[pos_a]
                for pos_b in range(pos_a + 1, len(team_matches)):
                    j = team_matches[pos_b]
                    for r in range(target_rows):
                        i_at_r = sum(x[(i, r, p)] for p in range(num_pitches))
                        for d in (-1, 0, 1):
                            r2 = r + d
                            if 0 <= r2 < target_rows:
                                j_at_r2 = sum(x[(j, r2, p)] for p in range(num_pitches))
                                model.Add(i_at_r + j_at_r2 <= 1)

        # Minimize row movement from original schedule.
        deviation_vars = []
        for i, item in enumerate(matches):
            orig_row = min(int(item['orig_row']), target_rows - 1)
            diff = model.NewIntVar(-target_rows, target_rows, f'diff_{i}')
            abs_diff = model.NewIntVar(0, target_rows, f'abs_diff_{i}')
            model.Add(diff == row_vars[i] - orig_row)
            model.AddAbsEquality(abs_diff, diff)
            deviation_vars.append(abs_diff)

        model.Minimize(sum(deviation_vars))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15.0
        solver.parameters.num_search_workers = 8
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        assignments = []
        for i in range(num_matches):
            placed = None
            for r in range(target_rows):
                for p in range(num_pitches):
                    if solver.Value(x[(i, r, p)]) == 1:
                        placed = (r, pitch_indexes[p])
                        break
                if placed:
                    break
            if placed is None:
                return None
            assignments.append((i, placed[0], placed[1]))

        return assignments

    def _apply_assignments(self, matches, assignments, target_rows):
        self.DfEditor._resetMatchIndex()

        # Ensure enough rows.
        while len(self.schedule) < target_rows:
            self.schedule.loc[self.schedule.index.max() + 1 if len(self.schedule) else 0] = None

        # Clear all slots; keep dataframe object and columns intact.
        for pitch_ind in self.schedule.columns:
            self.schedule[pitch_ind] = None

        # Place solved matches.
        for i, row_ind, pitch_ind in assignments:
            self.schedule.iloc[row_ind, pitch_ind] = matches[i]['match']

    def Optimize(self, desired_slots):
        """Optimize schedule to desired slots using OR-Tools CP-SAT."""
        cp_model = _load_cp_model()
        if cp_model is None:
            raise ImportError('ortools is required for TournamentSchedulerDataframeOptimizerOrtools')

        if desired_slots <= 0:
            raise ValueError('desired_slots must be positive')

        self.DfEditor._resetMatchIndex()
        matches = self._collect_matches()
        if not matches:
            return

        pitch_indexes = [int(p) for p in self.schedule.columns]
        max_rows = max(len(self.schedule), desired_slots)

        # Try to satisfy desired_slots first; relax row count only if infeasible.
        best = None
        for target_rows in range(desired_slots, max_rows + 1):
            best = self._build_and_solve(matches, target_rows, pitch_indexes)
            if best is not None:
                self._apply_assignments(matches, best, target_rows)
                return

        raise RuntimeError('No feasible OR-Tools schedule found within current row bounds')
