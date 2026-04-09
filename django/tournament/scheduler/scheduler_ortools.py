from ortools.sat.python import cp_model

class TournamentSchedulerOrtools:
    def __init__(self, matches_qs, num_pitches, num_slots):
        self.matches_qs = list(matches_qs)
        self.num_pitches = num_pitches
        self.num_slots = num_slots

        if self.num_pitches <= 0:
            raise ValueError("num_pitches must be > 0")
        if self.num_slots <= 0:
            raise ValueError("num_slots must be > 0")

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self._model_built = False
        self.last_status = None
        self.last_status_name = None

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
        max_slot_delta = max(0, self.num_slots - 1)
        for team in range(self.num_teams):
            matches = self.matches_by_team[team]
            for i in range(len(matches)):
                for j in range(i + 1, len(matches)):
                    m1, m2 = matches[i], matches[j]
                    diff = self.model.NewIntVar(
                        -max_slot_delta,
                        max_slot_delta,
                        f"diff_{m1}_{m2}",
                    )
                    abs_diff = self.model.NewIntVar(0, max_slot_delta, f"abs_diff_{m1}_{m2}")
                    self.model.Add(diff == self.slot[m1] - self.slot[m2])
                    self.model.AddAbsEquality(abs_diff, diff)
                    self.model.Add(abs_diff >= 2)

    def division_phase_order(self):
        """Zachování pořadí zápasů v divizi podle phase_block"""
        for _, match_list in self.division_matches.items():
            matches_by_block = {}
            for match_idx, block in match_list:
                if block is None:
                    continue
                matches_by_block.setdefault(block, []).append(match_idx)

            ordered_blocks = sorted(matches_by_block.keys())
            for lower_i in range(len(ordered_blocks) - 1):
                for higher_i in range(lower_i + 1, len(ordered_blocks)):
                    lower_block = ordered_blocks[lower_i]
                    higher_block = ordered_blocks[higher_i]
                    for lower_match_idx in matches_by_block[lower_block]:
                        for higher_match_idx in matches_by_block[higher_block]:
                            self.model.Add(self.slot[lower_match_idx] < self.slot[higher_match_idx])

    def minimize_last_slot(self):
        """Minimalizace posledního využitého slotu"""
        last_slot = self.model.NewIntVar(0, self.num_slots - 1, "last_slot")
        for m in range(self.num_matches):
            self.model.Add(last_slot >= self.slot[m])
        self.model.Minimize(last_slot)

    def build_model(self):
        if self._model_built:
            return

        self.one_match_per_pitch()
        self.team_not_same_time()
        self.team_no_back_to_back()
        self.division_phase_order()
        self.minimize_last_slot()
        self._model_built = True

    # =========================
    # 4) SOLVE
    # =========================
    def solve(self, max_time_seconds=30, apply_constraints=True):
        if apply_constraints:
            self.build_model()
        self.solver.parameters.max_time_in_seconds = max_time_seconds
        status = self.solver.Solve(self.model)
        self.last_status = status

        status_name_map = {
            cp_model.UNKNOWN: "UNKNOWN",
            cp_model.MODEL_INVALID: "MODEL_INVALID",
            cp_model.FEASIBLE: "FEASIBLE",
            cp_model.INFEASIBLE: "INFEASIBLE",
            cp_model.OPTIMAL: "OPTIMAL",
        }
        self.last_status_name = status_name_map.get(status, f"STATUS_{status}")

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