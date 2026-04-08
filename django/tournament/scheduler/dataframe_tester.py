from .. import models
from ..models import TeamPlaceholder


class TournamentSchedulerDataframeTester:
    """
        testy nad dataframe
    """

    def __init__(self, schedule):
        """ init, predame dataframe"""
        self.schedule = schedule

#
    # def _hasConflict(self,match_ind,tph):
    #     """zkontroluje zda je v okoli radku match_ind konflikt pro dane tph"""
    #     self.tdf


    # kontrola dvou zapasu
    def has_conflict(self, m1, m2):
        if (self.is_match_instance(m1) and self.is_match_instance(m2)):
            for tph1 in [m1.home, m1.away, m1.referee]:
                for tph2 in [m2.home, m2.away, m2.referee]:
                    if tph1 == tph2:
                        if tph1 is not None:
                            team_name = tph1
                            if tph1 and tph1.team:
                                team_name = tph1.team.name
                            print("Problem match num #{} team {}".format(models.Schedule.objects.get(match=m1).game_number, team_name))

    def is_match_instance(self, m):
        """
            Vraci True pro instanci Match
        """
        return isinstance(m, models.Match)

    def df_find_conflict(self):
        # check all
        df = self.schedule
        for i in range(len(df) - 1):
            for p1 in range(len(df.columns)):
                for p2 in range(len(df.columns)):
                    m1 = df.iloc[i, p1]
                    m2 = df.iloc[i + 1, p2]
                    if m1 and m2:
                        self.has_conflict(m1, m2)

    def schedule_matches_only(self):
        """ schedule zafiltrovane jen na matche"""
        return self.schedule[self.schedule.map(lambda x: isinstance(x, models.Match))]

    def count_matches(self):
        """ pocty zapasu bez mezer po hristich"""
        return self.schedule_matches_only().count()

    def _getGroupMatchesDf(self, group):
        """vraci dataframe kde jsou jen zapasy skupiny z parametru"""
        return self.schedule.map(lambda m: m if isinstance(m, models.Match) and m.group == group else None)

    def _getTphMatchesDf(self, tph):
        """vraci dataframe kde jsou jen zapasy tph z parametru"""
        return self.schedule.map(lambda m: m if isinstance(m, models.Match) and (m.home == tph or m.away == tph or m.referee == tph) else None)

    def _getDivisionPhaseFirstMatchIdex(self, division, phase):
        """vraci match index prvniho zapasu pro divizi a phase z parametru"""
        return self.schedule.map(lambda m: m.group.phase if isinstance(m, models.Match) and (m.group.division == division and m.group.phase == phase) else None).dropna(how='all').index.min()

    def _getFreeSlotsDf(self):
        """ Vraci dataframe s prazdnymi hracimi sloty """
        return self.schedule.isna().map(lambda v: 1 if v else None)

    def _getNonMatchSlotsDf(self):
        """ Vraci dataframe se sloty kde nejsou zapasy """
        return self.schedule.map(lambda m: 1 if not isinstance(m, models.Match) else None)

    def _canPlaceTph(self, tph, df_index, surroundings=True):
        """ test, zda muzeme tph umistit na dany index a okolni radky

            tph         - tph testovaneho tymu
            df_index    - index zapasu
            surroundings- prohledavat radek nad a pod
        """
        # pokud tph nereprezentuje tym, muzeme ho umistit kamkoli
        if tph is None:
            return True
        # indexy zapasu ve kterych tym hraje, nebo piska
        match_indexes = self._getTphMatchesDf(tph).dropna(how='all').index
        # testujeme na index
        if df_index in match_indexes:
            return False
        # testujeme okoli
        if surroundings:
            for test_index in [df_index - 1, df_index + 1]:
                if test_index in match_indexes:
                    return False
        # pokud nenajdeme problem, muzeme tph umistit
        return True

    def _canPlaceMatch(self, match, df_index, surroundings=True):
        """ Muzeme zapas umistit na dany radek?
            match         - match
            df_index    - index zapasu
            surroundings- prohledavat radek nad a pod
        """
        if isinstance(match, models.Match):
            for tph in [match.home, match.away, match.referee]:
                if isinstance(tph, TeamPlaceholder) and not self._canPlaceTph(tph, df_index, surroundings):
                    return False
        return True

    def _canShiftMatch(self, next_match, match_ind):
        # pokud next_match neni match
        if not isinstance(next_match, models.Match):
            # pokud v bunce neco je (asi pauza), nesmime posouvat
            if next_match:
                print("Match {} nelze posunout na {} (_canShiftMatch)".format(next_match, match_ind))
                return False
            # pokud v bunce nneni nic, muzeme posouvat
            else:
                return True
        else:
            # u indexu 0 jsem v pohode
            if match_ind == 0:
                return True
            # musime otestovat, jestli tymy nejsou na predchozim radku
            else:
                # zkoumam vsechny tymy
                for tph in [next_match.home, next_match.away, next_match.referee]:
                    # jen doplnene tymy
                    if tph is None:
                        continue
                    # zjistuji, jestli tph neni na predchozim radku
                    if match_ind - 1 in self._getTphMatchesDf(tph).dropna(how='all').index:
                        return False
                return True
