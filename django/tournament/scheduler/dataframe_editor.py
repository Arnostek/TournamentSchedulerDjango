from .. import models

from .dataframe_tester import TournamentSchedulerDataframeTester


class TournamentSchedulerDataframeEditor:
    """
        zakladni operace nad dataframe
    """

    def __init__(self, schedule):
        """ init, predame dataframe"""
        self.schedule = schedule
        self.DfTester = TournamentSchedulerDataframeTester(self.schedule)

    def _switchMatches(self, old, new):
        """ Prohozeni obsahu bunek
            old a new jsou souradnice ve tvaru (match_index,pitch_index)
        """
        old_val = self.schedule.iloc[old[0], old[1]]
        self.schedule.iloc[old[0], old[1]] = self.schedule.iloc[new[0], new[1]]
        self.schedule.iloc[new[0], new[1]] = old_val

    def _insert_match(self, match, match_ind):
        """ Insert match instance to row match_ind """
        # presouvame jen zapasy
        if not isinstance(match, models.Match):
            return
        # find empty place in schedule row
        row = self.schedule.iloc[match_ind, :]
        # prepiseme vse co neni zapas
        for pitch_ind in row[row.apply(lambda x: not isinstance(x, models.Match))].index:
            # insert match and return
            self.schedule.iloc[match_ind, pitch_ind] = match
            return

        # hriste s nejmensim poctem zapasu
        pitch2_ind = self.schedule.apply(lambda series: series.last_valid_index()).sort_values().index[0]
        # if target is match
        if isinstance(self.schedule.iloc[match_ind, pitch2_ind], models.Match):
            # add new row to end
            self.schedule.loc[self.schedule.index.max() + 1] = None
            # create space for match
            self.schedule.loc[match_ind:, pitch2_ind] = self.schedule.loc[match_ind:, pitch2_ind].shift()
            # add match
            self.schedule.loc[match_ind, pitch2_ind] = match

    def _insert_match_to_another_pitch(self, match_ind, pitch1_ind, pitch2_ind):
        """ move match to another pitch, create space if neccesary """
        # if target is match
        if isinstance(self.schedule.iloc[match_ind, pitch2_ind], models.Match):
            # add new row to end
            self.schedule.loc[self.schedule.index.max() + 1] = None
            # create space for match
            self.schedule.loc[match_ind:, pitch2_ind] = self.schedule.loc[match_ind:, pitch2_ind].shift()
            # move match to another pitch
        self._switchMatches((match_ind, pitch1_ind), (match_ind, pitch2_ind))

    def _shift_col(self, pitch_ind, match_ind):
        """ pokud je volne misto, posune bunky nahoru o jedno misto"""
        # posledni radek nema cenu posouvat
        if match_ind == self.schedule.index.max():
            return
        if self.schedule.isna().iloc[match_ind, pitch_ind]:
            # if there is match in cell above
            next_match = self.schedule.iloc[match_ind + 1, pitch_ind]
            if isinstance(next_match, models.Match):
                # we have to check possible Conflict
                if not self.DfTester._canShiftMatch(next_match, match_ind):
                    return
###### TODO - tady musime hlidat konflikty u vsech nasledujicich matchu, protoze se take posunou
            # ulozime si posunuty sloupec
            shifted = self.schedule[pitch_ind][match_ind:].shift(-1)
            # vymazeme radky smerem dolu
            self.schedule[pitch_ind] = self.schedule[pitch_ind][:match_ind]
            # updatneme dolni cast
            self.schedule.loc[match_ind:, pitch_ind] = shifted

    def _move_match_shift_col(self, match_ind, pitch1_ind, pitch2_ind):
        """ Presune zapas na jine hriste ve stejnem radku a pripadne posune zapasy"""
        self._switchMatches((match_ind, pitch1_ind), (match_ind, pitch2_ind))
        self._shift_col(pitch1_ind, match_ind)

    def _resetMatchIndex(self):
        """ Reset schedule match index"""
        self.schedule.reset_index(inplace=True, drop=True)
