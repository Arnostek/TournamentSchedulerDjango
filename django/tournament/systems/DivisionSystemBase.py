from .TournamentBuilders import (
    PhaseManager, PlacementBuilder, SemiFinalBuilder, 
    LastThreeBuilder, RefereeBuilder
)

class DivisionSystemBase:
    """ Zakladni trida, ze ktere se dedi tridy pro jednotlive systemy"""

    def __init__(self,tournament,division_name,division_slug,teams_count,semi,semi5_8=False,last3 = None,final_for = None,add_referees=True):
        """
            teams_count - pocet tymu
            semi        - semifinale pro 1-4
            semi5_8     - semifinale pro 5_8
            last3       - misto finalovych zapasu skupina pro posledni tri tymy
            final_for   - kolik tymu bude hrat finale
        """

        self.tournament = tournament
        self.teams_count = teams_count
        self._createDivision(division_name, division_slug, teams_count)
        self.add_referees  = add_referees

        # parametry generovani zapasu
        self.semi = semi
        self.semi5_8 = semi5_8

        # pro nezadane last3
        if last3 == None:
            # auto last3 pro liche pocty
            self.last3 = (teams_count % 2) == 1
        else:
            self.last3 = last3

        # od ktereho mista se bude hrat finale
        if final_for == None:
            if self.last3:
                self.final_for = teams_count - 3
            else:
                self.final_for = teams_count
        
        # Initialize builders for use in _createSystem()
        self._init_builders()

    def _init_builders(self):
        """Initialize builder instances for granular control."""
        self.phase = PhaseManager(self.division)
        self.placements = PlacementBuilder(self.phase)
        self.semis = SemiFinalBuilder(self.phase)
        self.last3_builder = LastThreeBuilder(self.phase)
        self.referees = RefereeBuilder(self.phase, self.division)

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
