class DivisionSystemBase:
    """ Zakladni trida, ze ktere se dedi tridy pro jednotlive systemy"""

    def __init__(self,tournament,division_name,division_slug,teams_count):

        self.tournament = tournament
        self.teams_count = teams_count
        self._createDivision(division_name, division_slug, teams_count)

    def _createDivision(self,name,slug,teams_count):

        self.division = self.tournament.division_set.create(name = name, slug = slug, teams = teams_count)

    def _createMatches(self):

        self.division.CreateMatches()

    def _lastMatchAddReferee(self,referee_tph):
        # najdeme posledni zapas a pridame rozhodciho
        m = self.division.match_set.last()
        if not m.referee:
            m.referee = referee_tph
            m.save()
