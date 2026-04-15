from tournament.models import Match
import pandas as pd

def build_slot_pitch_dataframe(result):
    """
    result = output from solver:
    [
        {
            "match_id": ...,
            "slot": ...,
            "pitch": ...
        }
    ]
    """

    # find matrix size
    max_slot = max(r["slot"] for r in result)
    max_pitch = max(r["pitch"] for r in result)

    # init empty grid
    grid = [
        [None for _ in range(max_pitch + 1)]
        for _ in range(max_slot + 1)
    ]

    # fill grid
    for r in result:
        s = r["slot"]
        p = r["pitch"]
        grid[s][p] = Match.objects.get(id=r["match_id"])

    # convert to dataframe
    df = pd.DataFrame(
        grid,
        index=range(max_slot + 1),
        columns=range(max_pitch + 1)
    )

    return df
