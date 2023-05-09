class DivisionSystemBase:
    """ Zakladni trida, ze ktere se dedi tridy pro jednotlive systemy"""

    def __init__(self,tournament,division_name,division_slug,teams_count,add_referees=True):

        self.tournament = tournament
        self.teams_count = teams_count
        self._createDivision(division_name, division_slug, teams_count)
        self.add_referees  = add_referees

    def _createDivision(self,name,slug,teams_count):

        self.division = self.tournament.division_set.create(name = name, slug = slug, teams = teams_count)

    def _createMatches(self):

        self.division.CreateMatches()

    def _GroupAddReferees(self, group_name, referees_tph):
        """ doplneni rozhodcich do zapasu skupiny """
        # najdeme group podle jmena
        group = self.division.GetGroup(group_name)
        # projdeme matche skupiny a pridame rozhodci
        for m in group.match_set.all():
            m.referee = referees_tph.pop()
            m.save()
