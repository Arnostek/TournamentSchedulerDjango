from collections import defaultdict
from ..models.match import Match

def build_solver_input(tid):
    """
    Django tournament → OR-Tools solver input

    OUTPUT:
    {
        "matches": [
            {
                "id": int,            # DB id (only for output mapping)
                "home": int,          # team id
                "away": int,          # team id
                "referee": int|None,  # team id
                "division": int,
                "phase": int,
                "order": int
            }
        ],
        "num_matches": int,
        "division_matches": {
            division_id: [match_index, match_index, ...]
        }
    }
    """

    matches = []
    division_matches = defaultdict(list)

    # =========================================================
    # BUILD MATCHES FROM DJANGO
    # =========================================================
    matches_queryset = Match.objects.select_related("division", "group", "home", "away", "referee").prefetch_related("group__grouprank_set").filter(division__tournament_id=tid).order_by("division_id", "group__phase", "phase_block", "id")


    for idx, m in enumerate(matches_queryset):

        matches.append({
            "id": m.id,
            "home": m.home_id,
            "away": m.away_id,
            "referee": m.referee_id,
            "group": m.group_id,
            "division": m.division_id,
            "phase": m.group.phase,
            "phase_block": m.phase_block,
            "order": m.id,
            "group_rank_placeholders": [gr.teamPlaceholder_id for gr in m.group.grouprank_set.all()],
        })

        # solver index (NOT DB id!)
        division_matches[m.division_id].append(idx)

    # =========================================================
    # SORT WITHIN DIVISIONS (IMPORTANT FOR ORDER CONSTRAINTS)
    # =========================================================
    for div_id in division_matches:
        division_matches[div_id].sort(
            key=lambda i: (
                matches[i]["phase"],
                matches[i]["phase_block"],
                matches[i]["order"],
            )
        )

    # convert defaultdict → dict (clean output)
    division_matches = dict(division_matches)

    # =========================================================
    # RETURN SOLVER INPUT
    # =========================================================
    return {
        "matches": matches,
        "num_matches": len(matches),
        "division_matches": division_matches,
    }