def polygon_generator(team_count):
    # poradi tymu v seedu
    seeds = [ i + 1 for i in range(team_count)]
    # pokud je sudy pocet, schovame si jeden tym vedle
    if (team_count % 2) == 0:
        evenIndex = seeds.pop()
    else:
        evenIndex = None
    # indexy zapasu
    matchIndexes = []

    # velikost polygonu
    size = len(seeds)

    # rotate size times
    for rotation in range(size):

        # rotate seeds
        seeds = seeds[-1:] + seeds[:-1]

        # extend matches list
        matchIndexes.extend(
            [
                (seeds[-1 * i - 1],seeds[i + 1])
                for i in range (size // 2)
            ]
        )

        # add one match for even index
        if (evenIndex != None):
            matchIndexes.extend(
                [
                    (seeds[0], evenIndex)
                ]
            )

    return matchIndexes
