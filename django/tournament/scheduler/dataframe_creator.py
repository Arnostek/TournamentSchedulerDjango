from .. import models
import pandas as pd


class TournamentSchedulerDataframeCreator:
    """ creates schedule dataframe from tournament matches """

    def __init__(self, tournament):
        """ constructor, returns pandas dataframe  """

        self.tournament = tournament
        self.schedule = pd.DataFrame([
            self._divisionMatchesWithPauses(division)
            for division in self.tournament.division_set.all().order_by('id')
        ]).T

    def _divisionMatchesWithPauses(self, division):
        """ returns matches list with necessary breaks in between """
        matches = []
        prev_match = None
        for match in division.match_set.all().order_by('group__phase', 'phase_block', 'id'):
            # mezi skupinami davam pauzu dva zapasy
            if self._needPause(prev_match, match):
                matches.append('Pauza - pocitani')
                # matches.append('Pauza - pocitani')
            # pri konfliktu zkusim odebrat rozhodciho
            if prev_match and not self._canFollow(prev_match, match):
                # zkusim odebrat rozhodciho
                ref = match.referee
                match.referee = None
                match.save()
                # pokud to nezabere, vratim rozhodciho a vlozim pauzu
                if not self._canFollow(prev_match, match):
                    match.referee = ref
                    match.save()
                    matches.append('Pauza - konflikt')
            # pridam zapas
            matches.append(match)
            prev_match = match
        return matches

    def _needPause(self, match1, match2):
        """ Returns True if we need to add break between matches"""
        if match1 is None:
            return False
        else:
            match1_ranks_tph = [
                grs.teamPlaceholder
                for grs in match1.group.grouprank_set.all()
            ]
            # pauza je potrebna pokud nejaky z tymu zavisi na poradi skupiny predchoziho zapasu
            # we need break when team depends on previous match result
            for tph in [match2.home, match2.away, match2.referee]:
                if tph in match1_ranks_tph:
                    return True
            # pauza je take  potrebna pri zmene phase
            if match1.group.phase != match2.group.phase:
                return True
            # pokud neni problem, neni pauza potreba
            return False

    def _canFollow(self, match1, match2):
        """ Muze match2 byt po matchi1 ?  """
        for tph1 in [match1.home, match1.away, match1.referee]:
            if tph1 is None:
                continue
            for tph2 in [match2.home, match2.away, match2.referee]:
                if tph2 is None:
                    continue
                if tph1 == tph2:
                    return False
        return True
