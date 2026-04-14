from collections import defaultdict
from ..models.match import Match

def build_solver_input(tid):
    """
    Django ORM → OR-Tools solver input (clean version)

    Assumptions:
    - home_id, away_id, referee_id are already INTs
    - no need for remapping teams
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
            # DB identity (only for output)
            "id": m.id,

            # solver-ready team IDs (already int)
            "home": m.home_id,
            "away": m.away_id,
            "referee": m.referee_id,

            # constraints metadata
            "division": m.division_id,
            "phase": getattr(m, "phase", 0),

            # ordering within division / tournament
            "order": getattr(m, "match_id", idx),
        })

        # =====================================================
        # DIVISION → solver index mapping
        # =====================================================
        division_matches[m.division_id].append(idx)

    # =========================================================
    # SORT DIVISIONS BY MATCH ORDER
    # =========================================================
    for div_id in division_matches:
        division_matches[div_id].sort(
            key=lambda i: matches[i]["order"]
        )

    # =========================================================
    # RETURN SOLVER INPUT
    # =========================================================
    return {
        "matches": matches,
        "num_matches": len(matches),

        # IMPORTANT for CP-SAT ordering constraints
        "division_matches": dict(division_matches),

        # optional debug
        "raw_queryset_count": len(matches),
    }