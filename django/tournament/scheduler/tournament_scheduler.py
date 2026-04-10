from .. import models

from .dataframe_creator import TournamentSchedulerDataframeCreator
from .dataframe_optimizer import TournamentSchedulerDataframeOptimizer


class TournamentScheduler:
    """
    vytvoreni hraciho planu
    """

    def __init__(self, tournament, pitches):
        """ konstruktor, predani turnaje ktery planujeme a poctu hrist """
        self.tournament = tournament
        self.pitches = pitches
        # create schedule from tournament matches
        tdc = TournamentSchedulerDataframeCreator(tournament)
        self.schedule = tdc.schedule
        # create optimizer
        self.tdo = TournamentSchedulerDataframeOptimizer(self.schedule)
        self.tdo._makeSameLength()

    def AddReferees(self):
        """ Pridani rozhodcich ke groupam, co maji referee_group"""
        for div in self.tournament.division_set.all():
            for gr in div.group_set.all():
                if gr.referee_group:
                    self._addRefereesGroup(gr)

    def _addRefereesGroup(self, group, refpool=None):
        """ Pridani rozhodcich dle referee group k jedne skupine """
        # pokud byl predan refpool
        if refpool:
            self.refPool = refpool
        # priravim si refPool
        else:
            # TODO dopredu vypocist velikost ref pool
            self._initRefPool(group.referee_group, 100)
        # df zapasy skupiny
        group_matches_df = self.tdo.DfTester._getGroupMatchesDf(group)
        # projdu zapasy skupiny
        for pitch in group_matches_df.columns:
            for match_ind in group_matches_df.index:
                match = group_matches_df.iloc[match_ind, pitch]
                if match:
                    if not match.referee:
                        # zkontrolujeme, zda tym muze piskat
                        for refPool_index in range(len(self.refPool)):
                        # TODO zbytecne prochazime cely pool, stacila by jedna obratka
                            if self.tdo.DfTester._canPlaceTph(self.refPool[refPool_index], match_ind):
                                match.referee = self.refPool.pop(refPool_index)
                                match.save()
                                break

    def _initRefPool(self, referee_group, match_count):
        """ Init refPool tymy z referee_group v parametru"""
        self.refPool = []
        while len(self.refPool) < match_count:
            self.refPool.extend([gs.teamPlaceholder for gs in referee_group.groupseed_set.all()])

    def _deleteEmptyRows(self):
        """ Delete empty schedule rows"""
        # smazeme prazdne radky
        # BUG - nekontrolujeme, zda je to mozne
        self.schedule.dropna(how='all', inplace=True)
        # reset indexu
        self.tdo.DfTester._resetMatchIndex()

    def DeleteSchedule(self):
        """ Delete schedule and pitches """
        self.tournament.schedule_set.all().delete()
        self.tournament.pitch_set.all().delete()

    def Schedule(self, times):
        """
            zalozeni schedule
        """
        # pocet sloupcu se musi shodovat s poctem hrist
        if len(self.schedule.columns) != self.pitches:
            raise ("Pocet hrist musi byt stejny jako pocet sloupcu schedule!")
        else:
            # zalozime hriste
            self.tournament.CreatePitches(self.pitches)
            # zalozime sloty pro zapasy
            for begin_end in times:
                self.tournament.CreateSchedules(begin_end[0], begin_end[1])
            # umistime zapasy do slotu
            for match_index in range(len(self.schedule)):
                for pitch_index in range(self.pitches):
                    if isinstance(self.schedule.iloc[match_index][pitch_index], models.Match):
                        sch = self.tournament.schedule_set.filter(pitch=self.tournament.pitch_set.all().order_by('id')[pitch_index])[match_index]
                        sch.match = self.schedule.iloc[match_index][pitch_index]
                        sch.save()
                    pitch_index += 1
                match_index += 1

    
    def ScheduleFromOrtools(self, times, ortools_result):
        """
        Create schedule from OR-Tools solver result.

        Args:
            times: list of (begin, end) datetime tuples, one per time slot,
                same format as Schedule()
            ortools_result: list of (match, slot_index, pitch_index) tuples
                            where slot_index is an index into `times` and
                            pitch_index is 0-based pitch number
        """
        # validate pitch count
        if len(self.schedule.columns) != self.pitches:
            raise ValueError("Pocet hrist musi byt stejny jako pocet sloupcu schedule!")

        # create pitches
        self.tournament.CreatePitches(self.pitches)

        # create schedule slots for each time entry
        for begin_end in times:
            self.tournament.CreateSchedules(begin_end[0], begin_end[1])

        # get ordered pitches and schedule slots
        pitches = list(self.tournament.pitch_set.all().order_by('id'))

        # place matches into slots based on OR-Tools assignments
        for match, slot_index, pitch_index in ortools_result:
            if not isinstance(match, models.Match):
                continue

            pitch = pitches[pitch_index]
            sch = self.tournament.schedule_set.filter(pitch=pitch)[slot_index]
            sch.match = match
            sch.save()

