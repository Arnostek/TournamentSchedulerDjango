from . import models
import pandas as pd
import numpy as np


class TournamentSchedulerDataframeCreator:
    """ creates schedule dataframe from tournament matches """
    def __init__(self,tournament):
        """ constructor, returns pandas dataframe  """

        self.tournament = tournament
        self.schedule =  pd.DataFrame([
            self._divisionMatchesWithPauses(division)
            for division in self.tournament.division_set.all().order_by('id')
        ]).T

    def _divisionMatchesWithPauses(self,division):
        """ returns matches list with necessary breaks in between """
        matches = []
        prev_match = None
        for match in division.match_set.all().order_by('group__phase','phase_block','id'):
            # mezi skupinami davam pauzu
            if self._needPause(prev_match,match):
                matches.append('Pauza - pocitani')
            # pri konfliktu davam Pauzu
            if prev_match and not self._canFollow(prev_match,match):
                matches.append('Pauza - konflikt')
            # pridam zapas
            matches.append(match)
            prev_match = match
        return matches

    def _needPause(self,match1,match2):
        """ Returns True if we need to add break between matches"""
        if match1 == None:
            return False
        else:
            match1_ranks_tph = [
                grs.teamPlaceholder
                for grs in match1.group.grouprank_set.all()
                ]
            # pauza je potrebna pokud nejaky z tymu zavisi na poradi skupiny predchoziho zapasu
            # we need break when team depends on previous match result
            for tph in [match2.home,match2.away,match2.referee]:
                if tph in match1_ranks_tph:
                    return True
            # pokud neni problem, neni pauza potreba
            return False

    def _canFollow(self,match1,match2):
        """ Muze match2 byt po matchi1 ?  """
        for tph1 in [match1.home,match1.away,match1.referee]:
            if tph1 == None:
                continue
            for tph2 in [match2.home,match2.away,match2.referee]:
                if tph2 == None:
                    continue
                if tph1 == tph2:
                    return False
        return True

class TournamentScheduler:
    """
    vytvoreni hraciho planu
    """

    def __init__(self,tournament,pitches):
        """ konstruktor, predani turnaje ktery planujeme a poctu hrist """
        self.tournament = tournament
        self.pitches = pitches
        # create schedule from tournament matches
        tdc = TournamentSchedulerDataframeCreator(tournament)
        self.schedule = tdc.schedule
        self._makeSameLength()
        self._reduceColumns()
        self._addReferees()

    def _switchMatches(self,old,new):
        """ Prohozeni obsahu bunek
            old a new jsou souradnice ve tvaru (match_index,pitch_index)
        """
        old_val = self.schedule.iloc[old[0],old[1]]
        self.schedule.iloc[old[0],old[1]] = self.schedule.iloc[new[0],new[1]]
        self.schedule.iloc[new[0],new[1]] = old_val

    def _shift_col(self,pitch_ind,match_ind):
        """ pokud je volne misto, posune bunky nahoru o jedno misto"""
        # posledni radek nema cenu posouvat
        if match_ind == self.schedule.index.max():
            return
        if self.schedule.isna().iloc[match_ind,pitch_ind]:
            # if there is match in cell above
            next_match = self.schedule.iloc[match_ind + 1,pitch_ind]
            if isinstance(next_match,models.Match):
                # we have to check possible Conflict
                if not self._canShiftMatch(next_match,match_ind):
                    return
###### TODO - tady musime hlidat konflikty u vsech nasledujicich matchu, protoze se take posunou
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

    def _insert_match_to_another_pitch(self, match_ind, pitch1_ind, pitch2_ind):
        """ move match to another pitch, create space if neccesary """
        # if target is match
        if isinstance(self.schedule.iloc[match_ind,pitch2_ind],models.Match):
            # add new row to end
            self.schedule.loc[self.schedule.index.max()+1] = None
            # create space for match
            self.schedule.loc[match_ind:,pitch2_ind] = self.schedule.loc[match_ind:,pitch2_ind].shift()
            # move match to another pitch
        self._switchMatches((match_ind,pitch1_ind),(match_ind,pitch2_ind))

    def _insert_match(self, match, match_ind):
        """ Insert match instance to row match_ind """
        if not isinstance(match, models.Match):
            return
        # find empty place in schedule row
        row = self.schedule.iloc[match_ind,:]
        # prepiseme vse co neni zapas
        for pitch_ind in row[row.apply(lambda x : not isinstance(x,models.Match))].index:
            # insert match and return
            self.schedule.iloc[match_ind,pitch_ind] = match
            return

        # hriste s nejmensim poctem zapasu
        pitch2_ind = self.schedule.apply(lambda series: series.last_valid_index()).sort_values().index[0]
        # if target is match
        if isinstance(self.schedule.iloc[match_ind,pitch2_ind],models.Match):
            # add new row to end
            self.schedule.loc[self.schedule.index.max()+1] = None
            # create space for match
            self.schedule.loc[match_ind:,pitch2_ind] = self.schedule.loc[match_ind:,pitch2_ind].shift()
            # add match
            self.schedule.loc[match_ind,pitch2_ind] = match

    def _makeSameLength(self):
        """ natahne vlozi mezery mezi zapasy tak, vsechny zapasy koncily stejne"""
        # projdeme hriste
        for pitch_index in self.schedule.columns:
            pocet_zapasu = self.schedule[pitch_index].count()

            if pocet_zapasu < len(self.schedule):
                # remove all spaces before lengthen
                self.schedule[pitch_index] = self.schedule[pitch_index].dropna().reset_index(drop=True)
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
                        # TODO zbytecne prochazime cely pool, stacila by jedna obratka
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
        return self.schedule.isna().applymap(lambda v : 1 if v else None)

    def _getNonMatchSlotsDf(self):
        """ Vraci dataframe se sloty kde nejsou zapasy """
        return self.schedule.applymap(lambda m : 1 if not isinstance(m,models.Match) else None)


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

    def _canPlaceMatch(self,match,df_index):
        """ Muzeme zapas umistit na dany radek? """
        for tph in [match.home,match.away,match.referee]:
            if not self._canPlaceTph(tph,df_index):
                return False
        return True

    def _canShiftMatch(self,next_match,match_ind):
        # pokud next_match neni match
        if not isinstance(next_match,models.Match):
            # pokud v bunce neco je (asi pauza), nesmime posouvat
            if next_match:
                return False
            # pokud v bunce nneni nic, muzeme posouvat
            else:
                return True
        else:
            # musime otestovat, jestli tymy nejsou na predchozim radku
            # u indexu 0 jsem v pohode
            if match_ind == 0:
                return True
            else:
                # zkoumam vsechny tymy
                for tph in [next_match.home,next_match.away,next_match.referee]:
                    # jen doplnene tymy
                    if tph == None:
                        continue
                    # zjistuji, jestli tph neni na predchozim radku
                    if match_ind -1 in self._getTphMatchesDf(tph).dropna(how='all').index:
                        return False
                return True

    def _reduceEmptySlots(self,desired_slots):
        """ zaplneni mezer v hracim planu """
        self._reduceEmptySlots01(desired_slots)
        self._reduceEmptySlots02(desired_slots)
        self._reduceEmptySlots03(desired_slots)

    def _deleteEmptyRows(self):
        """ Delete empty schedule rows"""
        # smazeme prazdne radky
        # BUG - nekontrolujeme, zda je to mozne
        self.schedule.dropna(how='all', inplace=True)
        # reset indexu
        self._resetMatchIndex()

    def _resetMatchIndex(self):
        """ Reset schedule match index"""
        self.schedule.reset_index(inplace=True,drop=True)

    def _reduceEmptySlots01(self,desired_slots):
        #nejdriv projdeme hriste, kde je zapasu min nebo rovno desired
        # reset indexu
        self._resetMatchIndex()
        # najdeme hriste, kde je zapasu min nebo rovno desired
        for pitch_ind in self.schedule.count()[self.schedule.count() <= desired_slots].sort_values().index:
            # staci smazat par mezer z konce
            # BUG pozor - musime testovat, zda to je mozne
            # najdeme volna mista ve schedule, od konce k zacatku
            for match_ind in self._getFreeSlotsDf()[pitch_ind].dropna().index.sort_values(ascending=False):
                # dokud je zapasu bez NA na konci vic nez desired
                if self.schedule[pitch_ind].last_valid_index() > desired_slots:
                    # redukujeme mezery
                    self._shift_col(pitch_ind,match_ind)

    def _reduceEmptySlots02(self,desired_slots):
        # u hrist kde je zapasu vic nez desired smazeme vsechny mezery
        self._resetMatchIndex()
        pitch_indexes = self.schedule.count()[self.schedule.count() > desired_slots].sort_values(ascending=False).index
        for pitch_ind in pitch_indexes:
            # smazeme vsechny prazdne - musime odzadu, jinak se nam cisla meni
            for match_ind in self._getFreeSlotsDf()[pitch_ind].dropna().index.sort_values(ascending=False):
                self._shift_col(pitch_ind,match_ind)

    def _reduceEmptySlots03(self,desired_slots):
        # projdeme radky az do delky dataframe
        self._resetMatchIndex()
        for match_ind in range(len(self.schedule)):
            # na kazdem radku hledame prazdna hriste
            for move_to_pitch_ind in self._getFreeSlotsDf().iloc[match_ind].dropna().index:
                # presouvame ze hrist s co nejvetsim poctem zapasu
                for pitch_ind in self.schedule.count().sort_values(ascending=False).index:
                    # pokud je na novem hristi mene zapasu a je potreba zmensovat
                    if (self.schedule.count()[pitch_ind] > self.schedule.count()[move_to_pitch_ind]) and (self.schedule.count()[pitch_ind] > desired_slots):
                        # najdeme si dalsi zapas
                        if match_ind >= len(self.schedule) -1:
                            next_match = None
                        else:
                            next_match = self.schedule.iloc[match_ind + 1, pitch_ind]
                            # pokud to nepujde posunout, jdeme na dalsi hriste
                            if not self._canShiftMatch(next_match,match_ind):
                                continue
                        # najdeme si nextnext zapas - ten se totiz taky dostane bliz
                        if match_ind >= len(self.schedule) -2:
                            next_next_match = None
                        else:
                            next_next_match = self.schedule.iloc[match_ind + 2, pitch_ind]
                            # pokud to nepujde posunout, jdeme na dalsi hriste
                            if not self._canShiftMatch(next_next_match,match_ind + 1):
                                continue
                        # pokud nam nic nezabranilo, posunujeme
                        self._move_match_shift_col(match_ind, pitch_ind, move_to_pitch_ind)
                        # ukoncime hledani hriste
                        break
            # pokud jsme dosahli cile, ukoncime optimalizaci
            if self.schedule.count().max() <= desired_slots:
                break
        # uplne nakonec vymazeme prazdne radky
        #self._deleteEmptyRows()


    def _reduceColumns(self):
        """ reduce columns to num of pitches """
        while len(self.schedule.columns) > self.pitches:
            # pitches sorted by count of matches
            # hriste s nejmene zapasy
            pitch_from = self.schedule.count().sort_values().index[0]
            # matches to move
            matches_to_move = self.schedule[pitch_from].dropna()
            # drop old column
            self.schedule.drop(columns = [pitch_from], inplace = True)
            # rename columns
            self.schedule.columns = [i for i in range(len(self.schedule.columns))]
            # reverse loop through matches
            for match_ind in matches_to_move.index.sort_values(ascending=False):
                self._insert_match(matches_to_move[match_ind], match_ind)
                matches_to_move[match_ind] = None

            # make same lengths again
            self._makeSameLength()

    def Optimize(self,desired_slots):
        """ Optimize schedule to desired slots """
        self._reduceEmptySlots(desired_slots)

    def DeleteSchedule(self):
        """ Delete schedule and pitches """
        self.tournament.schedule_set.all().delete()
        self.tournament.pitch_set.all().delete()


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
                        sch = self.tournament.schedule_set.filter(pitch = self.tournament.pitch_set.all().order_by('id')[pitch_index])[match_index]
                        sch.match = self.schedule.iloc[match_index][pitch_index]
                        sch.save()
                    pitch_index += 1
                match_index += 1
