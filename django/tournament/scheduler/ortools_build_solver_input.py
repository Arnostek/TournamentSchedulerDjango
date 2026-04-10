def build_solver_input():
    """
    Připraví a vrátí kompletní vstupní datovou strukturu pro OR-Tools solver.

    Načte všechny zápasy daného turnaje z databáze, přiřadí jim celočíselné
    indexy (požadované solverem) a sestaví pomocné mapy pro rychlé vyhledávání
    zápasů podle týmu, rozhodčího, divize, skupiny a fáze.

    Všechny DB primární klíče (int) jsou převedeny na kompaktní 0-based indexy,
    aby je bylo možné přímo použít jako proměnné / indexy polí v CP-SAT modelu.

    Returns:
        dict s klíči:
            matches            – seznam slovníků, každý popisuje jeden zápas
                                 (indexované hodnoty, ne DB ID)
            num_matches (M)    – celkový počet zápasů
            num_teams   (T)    – celkový počet unikátních týmů (vč. rozhodčích)
            teams              – seřazený seznam DB ID týmů
            team_idx           – DB ID týmu → jeho 0-based index
            divisions          – seřazený seznam DB ID divizí
            division_idx       – DB ID divize → její 0-based index
            groups             – seřazený seznam DB ID skupin
            group_idx          – DB ID skupiny → její 0-based index
            matches_by_team    – index týmu  → [indexy zápasů, v nichž hraje]
            matches_by_referee – index týmu  → [indexy zápasů, v nichž rozhoduje]
            matches_by_division– index divize → [indexy zápasů v divizi]
            matches_by_group   – index skupiny → [indexy zápasů ve skupině]
            matches_by_phase   – phase_block   → [indexy zápasů ve fázi]
            match_idx_to_db_id – 0-based index zápasu → původní DB ID
    """
    from collections import defaultdict
    from ..models.match import Match

    # ------------------------------------------------------------------
    # 1) Načtení zápasů z DB
    # ------------------------------------------------------------------
    # select_related zajistí JOIN v jediném SQL dotazu a zabrání N+1 problému
    # při následném přístupu k atributům relací (division, group, home, away, referee).
    # Filtrujeme pouze zápasy patřící k turnaji s ID=2.
    # Řazení podle id garantuje deterministické pořadí → stabilní indexy.
    qs = (
        Match.objects
        .select_related("division", "group", "home", "away", "referee")
        .filter(division__tournament_id=2)
        .order_by("id")
    )
    # Materializujeme queryset do Pythonového seznamu – solver pracuje
    # s daty v paměti, ne s lazy querysetem.
    match_list = list(qs)

    # ------------------------------------------------------------------
    # 2) Indexace zápasů: DB ID → 0-based integer index
    # ------------------------------------------------------------------
    # OR-Tools potřebuje zápasy adresovat celými čísly od 0.
    # match_idx[db_id] = solver_index
    match_idx = {m.id: i for i, m in enumerate(match_list)}

    # ------------------------------------------------------------------
    # 3) Sběr unikátních týmů (domácí + hosté + rozhodčí)
    # ------------------------------------------------------------------
    # Rozhodčí je v DB také tým (stejný model), proto ho zahrnujeme do
    # společného indexu. Referee může být None (zápas bez přiřazeného rozhodčího).
    team_ids = set()
    for m in match_list:
        team_ids.add(m.home_id)
        team_ids.add(m.away_id)
        if m.referee_id:
            team_ids.add(m.referee_id)

    # Seřazení zajistí stabilní, deterministické mapování mezi běhy.
    team_list = sorted(team_ids)
    # team_idx[db_id] = 0-based index týmu
    team_idx = {t: i for i, t in enumerate(team_list)}

    # ------------------------------------------------------------------
    # 4) Indexace divizí a skupin
    # ------------------------------------------------------------------
    # Stejný princip jako u týmů – kompaktní 0-based indexy pro solver.
    division_ids = sorted({m.division_id for m in match_list})
    division_idx = {d: i for i, d in enumerate(division_ids)}  # DB ID → index

    group_ids = sorted({m.group_id for m in match_list})
    group_idx = {g: i for i, g in enumerate(group_ids)}        # DB ID → index

    # ------------------------------------------------------------------
    # 5) Sestavení "flat" reprezentace zápasů
    # ------------------------------------------------------------------
    # Každý zápas je reprezentován slovníkem s čistě numerickými hodnotami
    # (0-based indexy). Solver tak nikdy nepracuje přímo s DB objekty.
    # Pole "db_id" si uchovává původní primární klíč pro zpětné uložení výsledků.
    matches_data = []

    for m in match_list:
        matches_data.append({
            "id":       match_idx[m.id],            # 0-based index zápasu pro solver
            "db_id":    m.id,                        # původní DB PK – slouží při ukládání výsledků zpět do DB
            "home":     team_idx[m.home_id],         # index domácího týmu
            "away":     team_idx[m.away_id],         # index hostujícího týmu
            "referee":  team_idx[m.referee_id] if m.referee_id else None,  # index rozhodčího (None = bez rozhodčího)
            "division": division_idx[m.division_id], # index divize
            "group":    group_idx[m.group_id],       # index skupiny
            "phase":    m.phase_block,               # fázový blok (např. "group_stage", "knockout") – zůstává jako string
        })

    # Zkratky používané v celém solveru (konvence: M = počet zápasů, T = počet týmů)
    M = len(matches_data)   # celkový počet zápasů
    T = len(team_list)      # celkový počet unikátních týmů / rozhodčích

    # ------------------------------------------------------------------
    # 6) Sestavení inverzních / pomocných map pro constraints
    # ------------------------------------------------------------------
    # Tyto mapy umožňují solveru efektivně formulovat omezení typu:
    #   "tým X nesmí hrát dvě kola za sebou" nebo
    #   "rozhodčí Y nesmí řídit dva zápasy ve stejném slotu".
    # Klíče jsou 0-based indexy, hodnoty jsou seznamy indexů zápasů.

    # Index týmu → seznam indexů všech zápasů, v nichž daný tým hraje (home nebo away)
    matches_by_team = defaultdict(list)

    # Index týmu → seznam indexů zápasů, v nichž daný tým působí jako rozhodčí
    matches_by_referee = defaultdict(list)

    # Index divize → seznam indexů všech zápasů v dané divizi
    matches_by_division = defaultdict(list)

    # Index skupiny → seznam indexů všech zápasů v dané skupině
    matches_by_group = defaultdict(list)

    # Fázový blok (string) → seznam indexů zápasů v dané fázi turnaje
    matches_by_phase = defaultdict(list)

    for m in matches_data:
        mid = m["id"]  # 0-based index tohoto zápasu

        # Domácí i hosté jsou oba "hráčskými" týmy → přidáme pro oba
        matches_by_team[m["home"]].append(mid)
        matches_by_team[m["away"]].append(mid)

        # Rozhodčí je volitelný – přidáme jen pokud je přiřazen
        if m["referee"] is not None:
            matches_by_referee[m["referee"]].append(mid)

        matches_by_division[m["division"]].append(mid)
        matches_by_group[m["group"]].append(mid)
        matches_by_phase[m["phase"]].append(mid)

    # ------------------------------------------------------------------
    # 7) Výstupní struktura pro solver
    # ------------------------------------------------------------------
    # defaultdict převedeme na obyčejný dict – zabraňujeme nechtěné tvorbě
    # nových klíčů při pozdějším přístupu (fail-fast chování je žádoucí).
    return {
        # Plný seznam zápasů s indexovanými hodnotami
        "matches": matches_data,

        # Skalární rozměry modelu
        "num_matches": M,
        "num_teams":   T,

        # Překlady index ↔ DB ID pro týmy
        "teams":    team_list,   # index → DB ID
        "team_idx": team_idx,    # DB ID → index

        # Překlady index ↔ DB ID pro divize
        "divisions":    division_ids,   # index → DB ID
        "division_idx": division_idx,   # DB ID → index

        # Překlady index ↔ DB ID pro skupiny
        "groups":    group_ids,   # index → DB ID
        "group_idx": group_idx,   # DB ID → index

        # Inverzní mapy – klíčové pro formulaci omezení (constraints) v solveru
        "matches_by_team":     dict(matches_by_team),
        "matches_by_referee":  dict(matches_by_referee),
        "matches_by_division": dict(matches_by_division),
        "matches_by_group":    dict(matches_by_group),
        "matches_by_phase":    dict(matches_by_phase),

        # Zpětné mapování solver index → DB ID (nutné při ukládání výsledků)
        "match_idx_to_db_id": {i: m.id for i, m in enumerate(match_list)},
    }
