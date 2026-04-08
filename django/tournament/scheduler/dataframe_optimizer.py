import numpy as np

from .. import models
from .dataframe_editor import TournamentSchedulerDataframeEditor


class TournamentSchedulerDataframeOptimizer:
    """
        optimalizace dataframe
    """

    def __init__(self, schedule):
        """ init, predame dataframe"""
        self.schedule = schedule
        self.DfEditor = TournamentSchedulerDataframeEditor(self.schedule)
        self.DfTester = self.DfEditor.DfTester

    # def

    def _makeSameLength(self):
        """ natahne vlozi mezery mezi zapasy tak, vsechny zapasy koncily stejne"""
        # projdeme hriste
        for pitch_index in self.schedule.columns:
            # spocteme zapasy
            pocet_zapasu = self.schedule[pitch_index].count()
            # pokud je zapasu mene nez delka df
            if pocet_zapasu < len(self.schedule):
                # remove all spaces before lengthen
                self.schedule[pitch_index] = self.schedule[pitch_index].dropna().reset_index(drop=True)
                old_index = pocet_zapasu - 1
                for new_index in np.flip(np.linspace(0, len(self.schedule) - 1, pocet_zapasu, dtype=int)):
                    if old_index != new_index:
                        self.DfEditor._switchMatches((old_index, pitch_index), (new_index, pitch_index))
                    old_index -= 1

    def _reduceColumns(self, pitches):
        """ reduce columns to num of pitches """
        while len(self.schedule.columns) > pitches:
            # pitches sorted by count of matches
            # hriste s nejmene zapasy
            pitch_from = self.schedule.count().sort_values().index[0]
            # matches to move
            matches_to_move = self.schedule[pitch_from].dropna()
            # drop old column
            self.schedule.drop(columns=[pitch_from], inplace=True)
            # rename columns
            self.schedule.columns = [i for i in range(len(self.schedule.columns))]
            # reverse loop through matches
            for match_ind in matches_to_move.index.sort_values(ascending=False):
# chybi test zda je to mozne
                self.DfEditor._insert_match(matches_to_move[match_ind], match_ind)
                matches_to_move[match_ind] = None

            # make same lengths again
            self._makeSameLength()

    def _reduceColumnsOnePitch(self, pitches):
        """ reduce columns to num of pitches
            vhodne jen pro nektere systemy
            idealne kdyz je jen o jedno hriste mene nez divizi a existuji dve skupiny se malym poctem zapasu
        """
        while len(self.schedule.columns) > pitches:
            # pitches sorted by count of matches
            # hriste s nejmene zapasy
            pitch_from = self.DfTester.count_matches().sort_values().index[0]
            pitch_to = self.DfTester.count_matches().sort_values().index[1]
            # matches to move - zapasy ze stareho hriste
            matches_to_move = self.DfTester.schedule_matches_only()[pitch_from].dropna()
            # reverse loop through matches
            for match_ind in matches_to_move.index.sort_values(ascending=False):
                # postupne presouvame na nove hriste
                self.DfEditor._insert_match_to_another_pitch(match_ind, pitch_from, pitch_to)
                matches_to_move[match_ind] = None
            # drop old column
            self.schedule.drop(columns=[pitch_from], inplace=True)
            # rename columns
            self.schedule.columns = [i for i in range(len(self.schedule.columns))]
            # make same lengths again
            self._makeSameLength()

    def _reduceEmptySlots01(self, desired_slots):
        # nejdriv projdeme hriste, kde je zapasu min nebo rovno desired
        # reset indexu
        print("--- _reduceEmptySlots01")
        self.DfEditor._resetMatchIndex()
        # najdeme hriste, kde je zapasu min nebo rovno desired
        for pitch_ind in self.schedule.count()[self.schedule.count() <= desired_slots].sort_values().index:
            # staci smazat par mezer z konce
            # BUG pozor - musime testovat, zda to je mozne
            # najdeme volna mista ve schedule, od konce k zacatku
            for match_ind in self.DfTester._getFreeSlotsDf()[pitch_ind].dropna().index.sort_values(ascending=False):
                # dokud je zapasu bez NA na konci vic nez desired
                if self.schedule[pitch_ind].last_valid_index() > desired_slots:
                    # redukujeme mezery
                    print("_shift_col Pitch: {}, match: {}".format(pitch_ind, match_ind))
                    self.DfEditor._shift_col(pitch_ind, match_ind)

    def _reduceEmptySlots02(self, desired_slots):
        # u hrist kde je zapasu vic nez desired smazeme vsechny mezery
        print("--- _reduceEmptySlots02")
        self.DfEditor._resetMatchIndex()
        pitch_indexes = self.schedule.count()[self.schedule.count() > desired_slots].sort_values(ascending=False).index
        for pitch_ind in pitch_indexes:
            # smazeme vsechny prazdne - musime odzadu, jinak se nam cisla meni
            for match_ind in self.DfTester._getFreeSlotsDf()[pitch_ind].dropna().index.sort_values(ascending=False):
                print("_shift_col Pitch: {}, match: {}".format(pitch_ind, match_ind))
                self.DfEditor._shift_col(pitch_ind, match_ind)

    def _reduceEmptySlots03(self, desired_slots, dont_move_to_pitch_index=None):
        # projdeme radky az do delky dataframe
        print("--- _reduceEmptySlots03")
        self.DfEditor._resetMatchIndex()
        for match_ind in range(len(self.schedule)):
            # na kazdem radku hledame prazdna hriste
            for move_to_pitch_ind in self.DfTester._getNonMatchSlotsDf().iloc[match_ind].dropna().index:
                # na hriste ze senamu nic nepresouvame
                if dont_move_to_pitch_index and move_to_pitch_ind in dont_move_to_pitch_index:
                    continue
                # presouvame ze hrist s co nejvetsim poctem zapasu
                for pitch_ind in self.schedule.count().sort_values(ascending=False).index:
                    # pokud je na novem hristi mene zapasu a je potreba zmensovat
                    current_match = self.schedule.iloc[match_ind][pitch_ind]
                    if (isinstance(current_match, models.Match) and self.schedule.count()[pitch_ind] > self.schedule.count()[move_to_pitch_ind]) and (self.schedule.count()[pitch_ind] > desired_slots):
                        # 1. zapas z phase neposouvame
                        if self.DfTester._getDivisionPhaseFirstMatchIdex(current_match, current_match.group.phase) == match_ind:
                            print("Neposouvame match (phase 1st match) - Pitch: {}, match: {}".format(pitch_ind, match_ind))
                            continue

                        # najdeme si dalsi zapas
                        if match_ind >= len(self.schedule) - 1:
                            next_match = None
                        else:
                            next_match = self.schedule.iloc[match_ind + 1, pitch_ind]
                            if isinstance(next_match, models.Match):
                                if next_match.group.phase != current_match.group.phase:
                                    print("Neposouvame match (zmena phase) - Pitch: {}, match: {}".format(pitch_ind, match_ind))
                                    continue

                            # pokud to nepujde posunout, jdeme na dalsi hriste
                            if not self.DfTester._canShiftMatch(next_match, match_ind):
                                print("Neprosel next_match - Pitch: {}, match: {}".format(pitch_ind, match_ind))
                                continue
                        # najdeme si nextnext zapas - ten se totiz taky dostane bliz
                        if match_ind >= len(self.schedule) - 2:
                            next_next_match = None
                        else:
                            next_next_match = self.schedule.iloc[match_ind + 2, pitch_ind]
                            # hledame, zda neni konflikt na radku match_ind. Na match_ind + 1 by byt nemel, protoze jinak by byl uz predtim.
                            # neproverujeme surroundings, protoze bychom nasli sami sebe
                            if not self.DfTester._canPlaceMatch(next_next_match, match_ind, surroundings=False):
                                print("Neprosel next_next_match - Pitch: {}, match: {}".format(pitch_ind, match_ind))
                                continue
                        # pokud nam nic nezabranilo, posunujeme
                        print("_move_match_shift_col Pitch: {}, match: {}, to_pitch: {}".format(pitch_ind, match_ind, move_to_pitch_ind))
                        # pokud je na cilovem hristi pauza, smazeme ji
                        if not isinstance(self.schedule.iloc[match_ind, move_to_pitch_ind], models.Match):
                            self.schedule.iloc[match_ind, move_to_pitch_ind] = np.nan
                        self.DfEditor._move_match_shift_col(match_ind, pitch_ind, move_to_pitch_ind)
                        # ukoncime hledani hriste
                        break
            # pokud jsme dosahli cile, ukoncime optimalizaci
            if self.schedule.count().max() <= desired_slots:
                break
        # uplne nakonec vymazeme prazdne radky
        #self._deleteEmptyRows()

    def Optimize(self, desired_slots):
        """ Optimize schedule to desired slots """
        self._reduceEmptySlots01(desired_slots)
        self._reduceEmptySlots02(desired_slots)
        self._reduceEmptySlots03(desired_slots)
