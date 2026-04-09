def build_solver_input():
    from collections import defaultdict
    from ..models.match import Match

    # 1) Načtení dat (optimalizované)
    qs = (
        Match.objects
        .select_related("division", "group", "home", "away", "referee")
        .filter(
            division__tournament_id=2
        )
    )
    match_list = list(qs)

    # 2) Indexace zápasů
    match_idx = {m.id: i for i, m in enumerate(match_list)}

    # 3) Sběr týmů (včetně rozhodčích)
    team_ids = set()
    for m in match_list:
        team_ids.add(m.home_id)
        team_ids.add(m.away_id)
        if m.referee_id:
            team_ids.add(m.referee_id)

    team_list = sorted(team_ids)
    team_idx = {t: i for i, t in enumerate(team_list)}

    # 4) Sběr divisions a groups
    division_ids = sorted({m.division_id for m in match_list})
    division_idx = {d: i for i, d in enumerate(division_ids)}

    group_ids = sorted({m.group_id for m in match_list})
    group_idx = {g: i for i, g in enumerate(group_ids)}

    # 5) Flat matches_data
    matches_data = []

    for m in match_list:
        matches_data.append({
            "id": match_idx[m.id],
            "db_id": m.id,  # pro zpětné uložení výsledků
            "home": team_idx[m.home_id],
            "away": team_idx[m.away_id],
            "referee": team_idx[m.referee_id] if m.referee_id else None,
            "division": division_idx[m.division_id],
            "group": group_idx[m.group_id],
            "phase": m.phase_block,
        })

    M = len(matches_data)
    T = len(team_list)

    # 6) Pomocné struktury

    # zápasy podle týmu
    matches_by_team = defaultdict(list)

    # zápasy podle rozhodčího
    matches_by_referee = defaultdict(list)

    # zápasy podle division
    matches_by_division = defaultdict(list)

    # zápasy podle group
    matches_by_group = defaultdict(list)

    # zápasy podle phase
    matches_by_phase = defaultdict(list)

    for m in matches_data:
        mid = m["id"]

        matches_by_team[m["home"]].append(mid)
        matches_by_team[m["away"]].append(mid)

        if m["referee"] is not None:
            matches_by_referee[m["referee"]].append(mid)

        matches_by_division[m["division"]].append(mid)
        matches_by_group[m["group"]].append(mid)
        matches_by_phase[m["phase"]].append(mid)

    # 7) Výstupní struktura
    return {
        "matches": matches_data,

        "num_matches": M,
        "num_teams": T,

        "teams": team_list,
        "team_idx": team_idx,

        "divisions": division_ids,
        "division_idx": division_idx,

        "groups": group_ids,
        "group_idx": group_idx,

        # pomocné mapy (klíčové pro constraints)
        "matches_by_team": dict(matches_by_team),
        "matches_by_referee": dict(matches_by_referee),
        "matches_by_division": dict(matches_by_division),
        "matches_by_group": dict(matches_by_group),
        "matches_by_phase": dict(matches_by_phase),

        # mapování zpět do DB
        "match_idx_to_db_id": {i: m.id for i, m in enumerate(match_list)},
    }