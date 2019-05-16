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

    def _maxSchedule(self):
        """
            vytvoreni maximalniho hraciho planu - vsechny zapasy za sebou, co divize to hriste
        """
        self.schedule = pd.DataFrame([
                [match
                for match in division.match_set.all().order_by('group__phase','phase_block','id')]
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
                    sch = self.tournament.schedule_set.filter(pitch = self.tournament.pitch_set.all()[pitch_index])[match_index]
                    sch.match = self.schedule.iloc[match_index][pitch_index]
                    sch.save()
                    pitch_index += 1
                match_index += 1

# potrebne mezery
# natahnuti planu
# zkraceni planu - posun na dalsi hriste
