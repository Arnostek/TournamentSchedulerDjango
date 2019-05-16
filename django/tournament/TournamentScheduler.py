from . import models
import pandas as pd

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
