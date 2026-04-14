from collections import defaultdict
from ..models.match import Match

def build_solver_input(tid):
    """
    Django ORM → OR-Tools solver input (clean version)

    OUTPUT:
    {
        "matches": [...],
        "num_matches": int,
        "division_matches": {division_id: [solver_index,...]}
    }
    """

    matches = []
    division_matches = defaultdict(list)

    # =========================================================
    # DJANGO INPUT
    # =========================================================
    raw_matches = Match.objects.select_related("division", "group", "home", "away", "referee").filter(division__tournament_id=tid).order_by("id")

    # =========================================================
    # BUILD MATCH LIST
    # =========================================================
    for idx, m in enumerate(raw_matches):

        matches.append({
            # DB identity (for output mapping only)
            "id": m.id,

            # solver-ready integer IDs
            "home": m.home_id,
            "away": m.away_id,
            "referee": m.referee_id,

            # constraints metadata
            "division": m.division_id,
            "phase": getattr(m, "phase", 0),

            # ordering inside division / tournament
            "order": getattr(m, "match_id", idx),
        })

        # =====================================================
        # DIVISION → solver indices
        # =====================================================
        division_matches[m.division_id].append(idx)

    # =========================================================
    # SORT DIVISIONS (VERY IMPORTANT FOR STABILITY)
    # =========================================================
    for div_id in division_matches:
        division_matches[div_id].sort(
            key=lambda i: matches[i]["order"]
        )

    division_matches = dict(division_matches)

    # =========================================================
    # RETURN SOLVER INPUT
    # =========================================================
    return {
        "matches": matches,
        "num_matches": len(matches),

        # critical for ordering constraints in CP-SAT
        "division_matches": division_matches,
    }