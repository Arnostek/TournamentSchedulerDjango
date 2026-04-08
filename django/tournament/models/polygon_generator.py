# code for generating round robin group matches
# see https://nrich.maths.org/1443 for idea

def polygon_generator(team_count):
    """
        function returns list of match tuples as  [(home_seed_rank, away_seed_rank, rotation)]
    """
    # poradi tymu v seedu

    seeds = [ i + 1 for i in range(team_count)]
    # pokud je sudy pocet, schovame si jeden tym vedle
    # when there is even num of teams in group, we pop last team to var evenIndex
    if (team_count % 2) == 0:
        evenIndex = seeds.pop()
    else:
        evenIndex = None
    # result var
    matchIndexes = []

    # polygon size
    size = len(seeds)

    # rotate size times
    for rotation in range(size):

        # rotate seeds
        seeds = seeds[-1:] + seeds[:-1]

        # extend matches list
        matchIndexes.extend(
            [
                (seeds[-1 * i - 1] ,seeds[i + 1], rotation)
                for i in range (size // 2)
            ]
        )

        # add one match for even index
        if (evenIndex != None):
            matchIndexes.extend(
                [
                    # TODO - last even team is always "away"
                    (seeds[0], evenIndex, rotation)
                ]
            )

    return matchIndexes
