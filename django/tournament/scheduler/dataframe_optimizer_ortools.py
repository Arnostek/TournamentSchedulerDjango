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

    def _match_phase_key(self, match_obj):
        group = match_obj.group
        division = group.division
        division_id = getattr(division, 'pk', None)
        if division_id is None:
            division_id = id(division)
        return (int(division_id), group.phase)

    def _team_key(self, tph):
        # Stable key for model grouping. Prefer DB pk when available.
        pk = getattr(tph, 'pk', None)
        if pk is not None:
            return ('pk', int(pk))
        return ('obj', id(tph))

    def _build_and_solve(self, matches, target_rows, pitch_indexes, dont_move_to_pitch_index=None):
        cp_model = _load_cp_model()
        if cp_model is None:
            return None

        model = cp_model.CpModel()
        num_matches = len(matches)
        num_pitches = len(pitch_indexes)
        blocked_pitches = set(dont_move_to_pitch_index or [])

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

        # Optionally block target pitches from receiving any moved/assigned matches.
        if blocked_pitches:
            for i in range(num_matches):
                for p, pitch_index in enumerate(pitch_indexes):
                    if pitch_index in blocked_pitches:
                        for r in range(target_rows):
                            model.Add(x[(i, r, p)] == 0)

        # Helper row vars for ordering and objective.
        row_vars = {}
        pitch_vars = {}
        for i in range(num_matches):
            row_var = model.NewIntVar(0, target_rows - 1, f'row_{i}')
            model.Add(row_var == sum(r * x[(i, r, p)] for r in range(target_rows) for p in range(num_pitches)))
            row_vars[i] = row_var

            pitch_var = model.NewIntVar(min(pitch_indexes), max(pitch_indexes), f'pitch_{i}')
            model.Add(
                pitch_var ==
                sum(pitch_indexes[p] * x[(i, r, p)] for r in range(target_rows) for p in range(num_pitches))
            )
            pitch_vars[i] = pitch_var

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

        # Keep first match of each (division, phase) on its original row when feasible.
        phase_first = {}
        for i, item in enumerate(matches):
            key = self._match_phase_key(item['match'])
            orig_row = int(item['orig_row'])
            if key not in phase_first or orig_row < phase_first[key][0]:
                phase_first[key] = (orig_row, i)
        for orig_row, i in phase_first.values():
            if orig_row < target_rows:
                model.Add(row_vars[i] == orig_row)

        # Keep ordering and at least one-row separation at phase boundaries per original pitch.
        for pitch, ordered in by_pitch.items():
            ordered.sort(key=lambda it: it[0])
            for idx in range(len(ordered) - 1):
                i1 = ordered[idx][1]
                i2 = ordered[idx + 1][1]
                m1 = matches[i1]['match']
                m2 = matches[i2]['match']
                if m1.group.phase != m2.group.phase:
                    model.Add(row_vars[i2] >= row_vars[i1] + 1)

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
        row_deviation_vars = []
        pitch_deviation_vars = []
        for i, item in enumerate(matches):
            orig_row = min(int(item['orig_row']), target_rows - 1)
            diff = model.NewIntVar(-target_rows, target_rows, f'diff_{i}')
            abs_diff = model.NewIntVar(0, target_rows, f'abs_diff_{i}')
            model.Add(diff == row_vars[i] - orig_row)
            model.AddAbsEquality(abs_diff, diff)
            row_deviation_vars.append(abs_diff)

            pitch_lo = max(pitch_indexes) - min(pitch_indexes)
            p_diff = model.NewIntVar(-pitch_lo, pitch_lo, f'p_diff_{i}')
            p_abs_diff = model.NewIntVar(0, pitch_lo, f'p_abs_diff_{i}')
            model.Add(p_diff == pitch_vars[i] - int(item['orig_pitch']))
            model.AddAbsEquality(p_abs_diff, p_diff)
            pitch_deviation_vars.append(p_abs_diff)

        # Row stability is primary; pitch stability is secondary.
        model.Minimize((100 * sum(row_deviation_vars)) + sum(pitch_deviation_vars))

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

    def Optimize(self, desired_slots, dont_move_to_pitch_index=None):
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
            best = self._build_and_solve(
                matches,
                target_rows,
                pitch_indexes,
                dont_move_to_pitch_index=dont_move_to_pitch_index,
            )
            if best is not None:
                self._apply_assignments(matches, best, target_rows)
                return

        raise RuntimeError('No feasible OR-Tools schedule found within current row bounds')
