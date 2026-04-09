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

        # --- matches by division
        self.division_matches = {}
        for idx, m in enumerate(self.matches_qs):
            div_id = m.division_id
            self.division_matches.setdefault(div_id, []).append((idx, m.phase_block))

    # =========================
    # 2) PROMĚNNÉ
    # =========================
    def _create_variables(self):
        # integer variables
        self.slot = [
            self.model.NewIntVar(0, self.num_slots - 1, f"slot_{m}")
            for m in range(self.num_matches)
        ]
        self.pitch = [
            self.model.NewIntVar(0, self.num_pitches - 1, f"pitch_{m}")
            for m in range(self.num_matches)
        ]

    # =========================
    # 3) CONSTRAINTY
    # =========================
    def one_match_per_pitch(self):
        """Na každém hřišti může být jen jeden zápas ve stejný slot"""
        for i in range(self.num_matches):
            for j in range(i + 1, self.num_matches):
                # pokud jsou na stejném hřišti, sloty musí být různé
                b = self.model.NewBoolVar(f"same_pitch_{i}_{j}")
                self.model.Add(self.pitch[i] == self.pitch[j]).OnlyEnforceIf(b)
                self.model.Add(self.pitch[i] != self.pitch[j]).OnlyEnforceIf(b.Not())
                self.model.Add(self.slot[i] != self.slot[j]).OnlyEnforceIf(b)

    def team_not_same_time(self):
        """Tým nemůže hrát více zápasů ve stejný slot"""
        for team in range(self.num_teams):
            matches = self.matches_by_team[team]
            for i in range(len(matches)):
                for j in range(i + 1, len(matches)):
                    m1, m2 = matches[i], matches[j]
                    self.model.Add(self.slot[m1] != self.slot[m2])

    def team_no_back_to_back(self):
        """Tým nesmí hrát dva zápasy po sobě (slot difference ≥ 2)"""
        for team in range(self.num_teams):
            matches = self.matches_by_team[team]
            for i in range(len(matches)):
                for j in range(i + 1, len(matches)):
                    m1, m2 = matches[i], matches[j]
                    diff = self.model.NewIntVar(-self.num_slots, self.num_slots, f"diff_{m1}_{m2}")
                    self.model.Add(diff == self.slot[m1] - self.slot[m2])
                    # nepovolíme |diff| = 1
                    b = self.model.NewBoolVar(f"back2back_ok_{m1}_{m2}")
                    self.model.Add(diff <= -2).OnlyEnforceIf(b)
                    self.model.Add(diff >= 2).OnlyEnforceIf(b)
                    self.model.AddBoolOr([b])

    def division_phase_order(self):
        """Zachování pořadí zápasů v divizi podle phase_block"""
        for div_id, match_list in self.division_matches.items():
            sorted_matches = sorted(match_list, key=lambda x: x[1])
            for i in range(len(sorted_matches) - 1):
                m1_idx, _ = sorted_matches[i]
                m2_idx, _ = sorted_matches[i + 1]
                self.model.Add(self.slot[m1_idx] < self.slot[m2_idx])

    def minimize_last_slot(self):
        """Minimalizace posledního využitého slotu"""
        last_slot = self.model.NewIntVar(0, self.num_slots - 1, "last_slot")
        for m in range(self.num_matches):
            self.model.Add(last_slot >= self.slot[m])
        self.model.Minimize(last_slot)

    # =========================
    # 4) SOLVE
    # =========================
    def solve(self, max_time_seconds=30):
        self.solver.parameters.max_time_in_seconds = max_time_seconds
        status = self.solver.Solve(self.model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        result = []
        for m in range(self.num_matches):
            result.append({
                "match_id": self.idx_to_match_id[m],
                "slot": self.solver.Value(self.slot[m]),
                "pitch": self.solver.Value(self.pitch[m])
            })
        return result