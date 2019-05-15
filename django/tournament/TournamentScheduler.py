from . import models

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
        self.schedule = [
                [match
                for match in division.match_set.all().order_by('group__phase','phase_block','id')]
            for division in self.tournament.division_set.all()
        ]

    #def _optimize

    def Schedule(self,times):
        """
            zalozeni schedule
        """
        # pocet sloupcu se musi shodovat s poctem hrist
        if len(self.schedule) != self.pitches:
            raise("Pocet hrist musi byt stejny jako pocet sloupcu schedule!")
        else:
            # zalozime hriste
            self.tournament.CreatePitches(self.pitches)
            # zalozime sloty pro zapasy
            for beg_eng in times:
                self.tournament.CreateSchedules(beg_eng[0],beg_eng[1])
            # umistime zapasy do slotu
            pitch_index = 0
            for pitch_matches in self.schedule:
                match_index = 0
                for match in pitch_matches:
                    sch = self.tournament.schedule_set.filter(pitch = self.tournament.pitch_set.all()[pitch_index])[match_index]
                    sch.match = match
                    sch.save()
                    match_index += 1

                pitch_index += 1

# potrebne mezery
# natahnuti planu
# zkraceni planu - posun na dalsi hriste
