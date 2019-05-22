from . import models
import pandas as pd
import numpy as np

class TournamentScheduler:
    """
    vytvoreni hraciho planu
    """

    def __init__(self,tournament,pitches):
        """ konstruktor, predani turnaje ktery planujeme a poctu hrist """
        self.tournament = tournament
        self.pitches = pitches
        #
        self._maxSchedule()
        self._addReferees()

    def _maxSchedule(self):
        """
            vytvoreni maximalniho hraciho planu - vsechny zapasy za sebou, co divize to hriste
        """
        self.schedule = pd.DataFrame([
            self._divisionMatchesWithPauses(division)
            for division in self.tournament.division_set.all()
        ]).T
        self._makeSameLength()

    def _switchMatches(self,old,new):
        """ Prohozeni obsahu bunek
            old a new jsou souradnice ve tvaru (match_index,pitch_index)
        """
        old_val = self.schedule.iloc[old[0],old[1]]
        self.schedule.iloc[old[0],old[1]] = self.schedule.iloc[new[0],new[1]]
        self.schedule.iloc[new[0],new[1]] = old_val

    def _shift_col(self,pitch_ind,match_ind):
        """ pokud je volne misto, posune bunky nahoru o jedno misto"""
        if not self.schedule.iloc[match_ind,pitch_ind]:
            # ulozime si posunuty sloupec
            shifted = self.schedule[pitch_ind][match_ind:].shift(-1)
            # vymazeme radky smerem dolu
            self.schedule[pitch_ind] = self.schedule[pitch_ind][:match_ind]
            # updatneme dolni cast
            self.schedule[pitch_ind][match_ind:].update(shifted)

    def _move_match_shift_col(self, match_ind, pitch1_ind, pitch2_ind):
        """ Presune zapas na jine hriste ve stejnem radku a pripadne posune zapasy"""
        self._switchMatches((match_ind,pitch1_ind),(match_ind,pitch2_ind))
        self._shift_col(pitch1_ind,match_ind)


    def _divisionMatchesWithPauses(self,division):
        """ list zapasu divize s povinnymi mezerami """
        matches = []
        prev_match = None
        for match in division.match_set.all().order_by('group__phase','phase_block','id'):
            if self._needPause(prev_match,match):
                matches.append('Pauza')
            matches.append(match)
            prev_match = match
        return matches

    def _needPause(self,match1,match2):
        """ Je potreba dat mezi zapasy pauzu ?"""
        if match1 == None:
            return False
        else:
            match1_ranks_tph = [
                grs.teamPlaceholder
                for grs in match1.group.grouprank_set.all()
                ]
            # pauza je potrebna pokud nejaky z tymu zavisi na poradi skupiny predchoziho zapasu
            for tph in [match2.home,match2.away,match2.referee]:
                if tph in match1_ranks_tph:
                    return True
            # pokud neni problem, neni pauza potreba
            return False

    def _makeSameLength(self):
        """ natahne vlozi mezery mezi zapasy tak, vsechny zapasy koncily stejne"""
        # projdeme hriste
        for pitch_index in range(self.pitches):
            pocet_zapasu = self.schedule[pitch_index].count()
            if pocet_zapasu < len(self.schedule):
                old_index = pocet_zapasu -1
                for new_index in np.flip(np.linspace(0,len(self.schedule)-1,pocet_zapasu,dtype=int)):
                    if (old_index != new_index):
                        self._switchMatches((old_index,pitch_index),(new_index,pitch_index))
                    old_index -= 1

    def _addReferees(self):
        """ Pridani rozhodcich ke groupam, co maji referee_group"""
        for div in self.tournament.division_set.all():
            for gr in div.group_set.all():
                if gr.referee_group:
                    self._addRefereesGroup(gr)

    def _addRefereesGroup(self,group):
        """ Pridani rozhodcich dle referee group k jedne skupine """
        # priravim si refPool
        # TODO dopredu vypocist velikost ref pool
        self._initRefPool(group.referee_group,100)
        # df zapasy skupiny
        group_matches_df = self._getGroupMatchesDf(group)
        # projdu zapasy skupiny
        for pitch in group_matches_df.columns:
            for match_ind in group_matches_df.index:
                match = group_matches_df.iloc[match_ind,pitch]
                if match:
                    if not match.referee:
                        # zkontrolujeme, zda tym muze piskat
                        for refPool_index in range(len(self.refPool)):
                            if self._canPlaceTph(self.refPool[refPool_index],match_ind):
                                match.referee = self.refPool.pop(refPool_index)
                                match.save()
                                break

    def _initRefPool(self,referee_group,match_count):
        """ Init refPool tymy z referee_group v parametru"""
        self.refPool = []
        while len(self.refPool) < match_count:
            self.refPool.extend([gs.teamPlaceholder for gs in referee_group.groupseed_set.all()])

    def _getGroupMatchesDf(self,group):
        """vraci dataframe kde jsou jen zapasy skupiny z parametru"""
        return self.schedule.applymap(lambda m : m if isinstance(m,models.Match) and m.group == group else None)

    def _getTphMatchesDf(self,tph):
        """vraci dataframe kde jsou jen zapasy tph z parametru"""
        return self.schedule.applymap(lambda m : m if isinstance(m,models.Match) and (m.home == tph or m.away == tph or m.referee == tph) else None)

    def _getFreeSlotsDf(self):
        """ Vraci dataframe s prazdnymi hracimi sloty """
        return self.schedule.applymap(lambda m : None if isinstance(m,models.Match) else 1)

    def _canPlaceTph(self,tph,df_index):
        """ test, zda muzeme tph umistit na dany index"""
        # indexy zapasu ve kterych tym hraje, nebo piska
        match_indexes = self._getTphMatchesDf(tph).dropna(how='all').index
        # testujeme na index a okoli
        for test_index in [df_index -1 , df_index, df_index +1]:
            if test_index in match_indexes:
                return False
        # pokud nenajdeme problem, muzeme tph umistit
        return True


    #def _optimize

    def Schedule(self,times):
        """
            zalozeni schedule
        """
        # pocet sloupcu se musi shodovat s poctem hrist
        if len(self.schedule.columns) != self.pitches:
            raise("Pocet hrist musi byt stejny jako pocet sloupcu schedule!")
        else:
            # zalozime hriste
            self.tournament.CreatePitches(self.pitches)
            # zalozime sloty pro zapasy
            for begin_end in times:
                self.tournament.CreateSchedules(begin_end[0],begin_end[1])
            # umistime zapasy do slotu
            for match_index in range(len(self.schedule)):
                for pitch_index in range(self.pitches):
                    if isinstance(self.schedule.iloc[match_index][pitch_index],models.Match):
                        sch = self.tournament.schedule_set.filter(pitch = self.tournament.pitch_set.all()[pitch_index])[match_index]
                        sch.match = self.schedule.iloc[match_index][pitch_index]
                        sch.save()
                    pitch_index += 1
                match_index += 1

# potrebne mezery
# natahnuti planu
# zkraceni planu - posun na dalsi hriste
