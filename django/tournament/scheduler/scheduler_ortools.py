from ortools.sat.python import cp_model

class TournamentSchedulerOrtools:
    def __init__(self, matches_qs, num_pitches, num_slots):
        self.matches_qs = list(matches_qs)
        self.num_pitches = num_pitches
        self.num_slots = num_slots

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

        self._prepare_indices()
        self._create_variables()

    # =========================
    # 1) INDEXACE
    # =========================
    def _prepare_indices(self):
        # --- team mapping
        team_ids = set()
        for m in self.matches_qs:
            team_ids.add(m.home_id)
            team_ids.add(m.away_id)
            if m.referee_id:
                team_ids.add(m.referee_id)
        self.team_id_to_idx = {tid: i for i, tid in enumerate(sorted(team_ids))}
        self.idx_to_team_id = {i: k for k, i in self.team_id_to_idx.items()}
        self.num_teams = len(self.team_id_to_idx)

        # --- match mapping
        self.num_matches = len(self.matches_qs)
        self.idx_to_match_id = {i: m.id for i, m in enumerate(self.matches_qs)}

        # --- home/away arrays
        self.home = [self.team_id_to_idx[m.home_id] for m in self.matches_qs]
        self.away = [self.team_id_to_idx[m.away_id] for m in self.matches_qs]

        # --- matches by team
        self.matches_by_team = {t: [] for t in range(self.num_teams)}
        for m in range(self.num_matches):
            self.matches_by_team[self.home[m]].append(m)
            self.matches_by_team[self.away[m]].append(m)

    # =========================
    # 2) PROMĚNNÉ
    # =========================
    def _create_variables(self):
        self.is_scheduled = {}
        for m in range(self.num_matches):
            for t in range(self.num_slots):
                for p in range(self.num_pitches):
                    self.is_scheduled[m, t, p] = self.model.NewBoolVar(
                        f"m{m}_t{t}_p{p}"
                    )

    # =========================
    # 3) CONSTRAINTY
    # =========================
    def each_match_once(self):
        for m in range(self.num_matches):
            self.model.Add(
                sum(
                    self.is_scheduled[m, t, p]
                    for t in range(self.num_slots)
                    for p in range(self.num_pitches)
                ) == 1
            )

    def one_match_per_pitch(self):
        for t in range(self.num_slots):
            for p in range(self.num_pitches):
                self.model.Add(
                    sum(self.is_scheduled[m, t, p] for m in range(self.num_matches)) <= 1
                )

    def team_not_same_time(self):
        for t in range(self.num_slots):
            for team in range(self.num_teams):
                self.model.Add(
                    sum(
                        self.is_scheduled[m, t, p]
                        for m in self.matches_by_team[team]
                        for p in range(self.num_pitches)
                    ) <= 1
                )

    def team_no_back_to_back(self):
        for team in range(self.num_teams):
            for t in range(self.num_slots - 1):
                plays_t = sum(
                    self.is_scheduled[m, t, p]
                    for m in self.matches_by_team[team]
                    for p in range(self.num_pitches)
                )
                plays_t1 = sum(
                    self.is_scheduled[m, t + 1, p]
                    for m in self.matches_by_team[team]
                    for p in range(self.num_pitches)
                )
                self.model.Add(plays_t + plays_t1 <= 1)

    # =========================
    # 4) OPTIMALIZACE
    # =========================
    def minimize_last_slot(self):
        last_slot = self.model.NewIntVar(0, self.num_slots - 1, "last_slot")
        for m in range(self.num_matches):
            for t in range(self.num_slots):
                for p in range(self.num_pitches):
                    self.model.Add(last_slot >= t).OnlyEnforceIf(self.is_scheduled[m, t, p])
        self.model.Minimize(last_slot)

    # =========================
    # 5) SOLVE
    # =========================
    def solve(self, max_time_seconds=30):
        self.solver.parameters.max_time_in_seconds = max_time_seconds
        status = self.solver.Solve(self.model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        result = []
        for m in range(self.num_matches):
            for t in range(self.num_slots):
                for p in range(self.num_pitches):
                    if self.solver.Value(self.is_scheduled[m, t, p]):
                        result.append({
                            "match_id": self.idx_to_match_id[m],
                            "slot": t,
                            "pitch": p
                        })
        return result