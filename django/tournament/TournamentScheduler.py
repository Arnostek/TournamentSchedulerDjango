from . import models
import pandas as pd
import numpy as np
from .models import TeamPlaceholder

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
            # mezi skupinami davam pauzu dva zapasy
            if self._needPause(prev_match,match):
                matches.append('Pauza - pocitani')
                # matches.append('Pauza - pocitani')
            # pri konfliktu zkusim odebrat rozhodciho
            if prev_match and not self._canFollow(prev_match,match):
                # zkusim odebrat rozhodciho
                ref = match.referee
                match.referee = None
                match.save()
                # pokud to nezabere, vratim rozhodciho a vlozim pauzu
                if not self._canFollow(prev_match,match):
                    match.referee = ref
                    match.save()
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
            # pauza je take  potrebna pri zmene phase
            if match1.group.phase != match2.group.phase:
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


class TournamentSchedulerDataframeOptimizer:
    """
        optimalizace dataframe
    """
    def __init__(self,schedule):
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
                old_index = pocet_zapasu -1
                for new_index in np.flip(np.linspace(0,len(self.schedule)-1,pocet_zapasu,dtype=int)):
                    if (old_index != new_index):
                        self.DfEditor._switchMatches((old_index,pitch_index),(new_index,pitch_index))
                    old_index -= 1

    def _reduceColumns(self,pitches):
        """ reduce columns to num of pitches """
        while len(self.schedule.columns) > pitches:
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
# chybi test zda je to mozne
                self.DfEditor._insert_match(matches_to_move[match_ind], match_ind)
                matches_to_move[match_ind] = None

            # make same lengths again
            self._makeSameLength()

    def _reduceColumnsOnePitch(self,pitches):
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
                self.DfEditor._insert_match_to_another_pitch(match_ind,pitch_from,pitch_to)
                matches_to_move[match_ind] = None
            # drop old column
            self.schedule.drop(columns = [pitch_from], inplace = True)
            # rename columns
            self.schedule.columns = [i for i in range(len(self.schedule.columns))]
            # make same lengths again
            self._makeSameLength()

    def _reduceEmptySlots01(self,desired_slots):
        #nejdriv projdeme hriste, kde je zapasu min nebo rovno desired
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
                    print("_shift_col Pitch: {}, match: {}".format(pitch_ind,match_ind))
                    self.DfEditor._shift_col(pitch_ind,match_ind)

    def _reduceEmptySlots02(self,desired_slots):
        # u hrist kde je zapasu vic nez desired smazeme vsechny mezery
        print("--- _reduceEmptySlots02")
        self.DfEditor._resetMatchIndex()
        pitch_indexes = self.schedule.count()[self.schedule.count() > desired_slots].sort_values(ascending=False).index
        for pitch_ind in pitch_indexes:
            # smazeme vsechny prazdne - musime odzadu, jinak se nam cisla meni
            for match_ind in self.DfTester._getFreeSlotsDf()[pitch_ind].dropna().index.sort_values(ascending=False):
                print("_shift_col Pitch: {}, match: {}".format(pitch_ind,match_ind))
                self.DfEditor._shift_col(pitch_ind,match_ind)

    def _reduceEmptySlots03(self,desired_slots):
        # projdeme radky az do delky dataframe
        print("--- _reduceEmptySlots03")
        self.DfEditor._resetMatchIndex()
        for match_ind in range(len(self.schedule)):
            # na kazdem radku hledame prazdna hriste
            for move_to_pitch_ind in self.DfTester._getNonMatchSlotsDf().iloc[match_ind].dropna().index:
                # presouvame ze hrist s co nejvetsim poctem zapasu
                for pitch_ind in self.schedule.count().sort_values(ascending=False).index:
                    # pokud je na novem hristi mene zapasu a je potreba zmensovat
                    current_match = self.schedule.iloc[match_ind][pitch_ind]
                    if (isinstance(current_match,models.Match) and self.schedule.count()[pitch_ind] > self.schedule.count()[move_to_pitch_ind]) and (self.schedule.count()[pitch_ind] > desired_slots):
                        # 1. zapas z phase neposouvame
                        if self.DfTester._getDivisionPhaseFirstMatchIdex(current_match,current_match.group.phase) == match_ind:
                            print("Neposouvame match (phase 1st match) - Pitch: {}, match: {}".format(pitch_ind,match_ind))
                            continue

                        # najdeme si dalsi zapas
                        if match_ind >= len(self.schedule) -1:
                            next_match = None
                        else:
                            next_match = self.schedule.iloc[match_ind + 1, pitch_ind]
                            if isinstance(next_match,models.Match):
                                if next_match.group.phase != current_match.group.phase:
                                    print("Neposouvame match (zmena phase) - Pitch: {}, match: {}".format(pitch_ind,match_ind))
                                    continue

                            # pokud to nepujde posunout, jdeme na dalsi hriste
                            if not self.DfTester._canShiftMatch(next_match,match_ind):
                                print("Neprosel next_match - Pitch: {}, match: {}".format(pitch_ind,match_ind))
                                continue
                        # najdeme si nextnext zapas - ten se totiz taky dostane bliz
                        if match_ind >= len(self.schedule) -2:
                            next_next_match = None
                        else:
                            next_next_match = self.schedule.iloc[match_ind + 2, pitch_ind]
                            # hledame, zda neni konflikt na radku match_ind. Na match_ind + 1 by byt nemel, protoze jinak by byl uz predtim.
                            # neproverujeme surroundings, protoze bychom nasli sami sebe
                            if not self.DfTester._canPlaceMatch(next_next_match,match_ind,surroundings=False):
                                print("Neprosel next_next_match - Pitch: {}, match: {}".format(pitch_ind,match_ind))
                                continue
                        # pokud nam nic nezabranilo, posunujeme
                        print("_move_match_shift_col Pitch: {}, match: {}, to_pitch: {}".format(pitch_ind,match_ind,move_to_pitch_ind))
                        # pokud je na cilovem hristi pauza, smazeme ji
                        if not isinstance(self.schedule.iloc[match_ind,move_to_pitch_ind],models.Match):
                            self.schedule.iloc[match_ind,move_to_pitch_ind] = np.nan
                        self.DfEditor._move_match_shift_col(match_ind, pitch_ind, move_to_pitch_ind)
                        # ukoncime hledani hriste
                        break
            # pokud jsme dosahli cile, ukoncime optimalizaci
            if self.schedule.count().max() <= desired_slots:
                break
        # uplne nakonec vymazeme prazdne radky
        #self._deleteEmptyRows()

    def Optimize(self,desired_slots):
        """ Optimize schedule to desired slots """
        self._reduceEmptySlots01(desired_slots)
        self._reduceEmptySlots02(desired_slots)
        self._reduceEmptySlots03(desired_slots)

class TournamentSchedulerDataframeEditor:
    """
        zakladni operace nad dataframe
    """
    def __init__(self,schedule):
        """ init, predame dataframe"""
        self.schedule = schedule
        self.DfTester = TournamentSchedulerDataframeTester(self.schedule)

    def _switchMatches(self,old,new):
        """ Prohozeni obsahu bunek
            old a new jsou souradnice ve tvaru (match_index,pitch_index)
        """
        old_val = self.schedule.iloc[old[0],old[1]]
        self.schedule.iloc[old[0],old[1]] = self.schedule.iloc[new[0],new[1]]
        self.schedule.iloc[new[0],new[1]] = old_val

    def _insert_match(self, match, match_ind):
        """ Insert match instance to row match_ind """
        # presouvame jen zapasy
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
                if not self.DfTester._canShiftMatch(next_match,match_ind):
                    return
###### TODO - tady musime hlidat konflikty u vsech nasledujicich matchu, protoze se take posunou
            # ulozime si posunuty sloupec
            shifted = self.schedule[pitch_ind][match_ind:].shift(-1)
            # vymazeme radky smerem dolu
            self.schedule[pitch_ind] = self.schedule[pitch_ind][:match_ind]
            # updatneme dolni cast
            self.schedule.loc[match_ind:,pitch_ind] = shifted

    def _move_match_shift_col(self, match_ind, pitch1_ind, pitch2_ind):
        """ Presune zapas na jine hriste ve stejnem radku a pripadne posune zapasy"""
        self._switchMatches((match_ind,pitch1_ind),(match_ind,pitch2_ind))
        self._shift_col(pitch1_ind,match_ind)

    def _resetMatchIndex(self):
        """ Reset schedule match index"""
        self.schedule.reset_index(inplace=True,drop=True)

class TournamentSchedulerDataframeTester:
    """
        testy nad dataframe
    """
    def __init__(self,schedule):
        """ init, predame dataframe"""
        self.schedule = schedule

#
    # def _hasConflict(self,match_ind,tph):
    #     """zkontroluje zda je v okoli radku match_ind konflikt pro dane tph"""
    #     self.tdf


    # kontrola dvou zapasu
    def has_conflict(self,m1,m2):
        if (self.is_match_instance(m1) and self.is_match_instance(m2)):
            for tph1 in [m1.home,m1.away,m1.referee]:
                for tph2 in [m2.home,m2.away,m2.referee]:
                    if tph1 == tph2:
                        if tph1 != None:
                            team_name = tph1
                            if tph1 and tph1.team:
                                team_name = tph1.team.name
                            print ("Problem match num #{} team {}".format(models.Schedule.objects.get(match=m1).game_number,team_name))

    def is_match_instance(self,m):
        """
            Vraci True pro instanci Match
        """
        return isinstance(m,models.Match)

    def df_find_conflict(self):
        # check all
        df = self.schedule
        for i in range(len(df)-1):
            for p1 in range(len(df.columns)):
                for p2 in range(len(df.columns)):
                    m1 = df.iloc[i,p1]
                    m2 = df.iloc[i+1,p2]
                    if m1 and m2:
                        self.has_conflict(m1,m2)


    def schedule_matches_only(self):
        """ schedule zafiltrovane jen na matche"""
        return self.schedule[self.schedule.map(lambda x : isinstance(x,models.Match))]

    def count_matches(self):
        """ pocty zapasu bez mezer po hristich"""
        return self.schedule_matches_only().count()

    def _getGroupMatchesDf(self,group):
        """vraci dataframe kde jsou jen zapasy skupiny z parametru"""
        return self.schedule.map(lambda m : m if isinstance(m,models.Match) and m.group == group else None)

    def _getTphMatchesDf(self,tph):
        """vraci dataframe kde jsou jen zapasy tph z parametru"""
        return self.schedule.map(lambda m : m if isinstance(m,models.Match) and (m.home == tph or m.away == tph or m.referee == tph) else None)

    def _getDivisionPhaseFirstMatchIdex(self,division,phase):
        """vraci match index prvniho zapasu pro divizi a phase z parametru"""
        return self.schedule.map(lambda m : m.group.phase if isinstance(m,models.Match) and (m.group.division == division and m.group.phase == phase) else None).dropna(how='all').index.min()

    def _getFreeSlotsDf(self):
        """ Vraci dataframe s prazdnymi hracimi sloty """
        return self.schedule.isna().map(lambda v : 1 if v else None)

    def _getNonMatchSlotsDf(self):
        """ Vraci dataframe se sloty kde nejsou zapasy """
        return self.schedule.map(lambda m : 1 if not isinstance(m,models.Match) else None)

    def _canPlaceTph(self,tph,df_index,surroundings=True):
        """ test, zda muzeme tph umistit na dany index a okolni radky

            tph         - tph testovaneho tymu
            df_index    - index zapasu
            surroundings- prohledavat radek nad a pod
        """
        # pokud tph nereprezentuje tym, muzeme ho umistit kamkoli
        if tph == None:
            return True
        # indexy zapasu ve kterych tym hraje, nebo piska
        match_indexes = self._getTphMatchesDf(tph).dropna(how='all').index
        # testujeme na index
        if df_index in match_indexes:
            return False
        # testujeme okoli
        if surroundings:
            for test_index in [df_index -1 , df_index +1]:
                if test_index in match_indexes:
                    return False
        # pokud nenajdeme problem, muzeme tph umistit
        return True

    def _canPlaceMatch(self,match,df_index,surroundings=True):
        """ Muzeme zapas umistit na dany radek?
            match         - match
            df_index    - index zapasu
            surroundings- prohledavat radek nad a pod
        """
        if isinstance(match, models.Match):
            for tph in [match.home,match.away,match.referee]:
                if isinstance(tph,TeamPlaceholder) and not self._canPlaceTph(tph,df_index,surroundings):
                    return False
        return True

    def _canShiftMatch(self,next_match,match_ind):
        # pokud next_match neni match
        if not isinstance(next_match,models.Match):
            # pokud v bunce neco je (asi pauza), nesmime posouvat
            if next_match:
                print("Match {} nelze posunout na {} (_canShiftMatch)".format(next_match,match_ind))
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
                for tph in [next_match.home,next_match.away,next_match.referee]:
                    # jen doplnene tymy
                    if tph == None:
                        continue
                    # zjistuji, jestli tph neni na predchozim radku
                    if match_ind -1 in self._getTphMatchesDf(tph).dropna(how='all').index:
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
        # create optimizer
        self.tdo = TournamentSchedulerDataframeOptimizer(self.schedule)
        self.tdo._makeSameLength()

    def AddReferees(self):
        """ Pridani rozhodcich ke groupam, co maji referee_group"""
        for div in self.tournament.division_set.all():
            for gr in div.group_set.all():
                if gr.referee_group:
                    self._addRefereesGroup(gr)

    def _addRefereesGroup(self,group,refpool=None):
        """ Pridani rozhodcich dle referee group k jedne skupine """
        # pokud byl predan refpool
        if refpool:
            self.refPool = refpool
        # priravim si refPool
        else:
            # TODO dopredu vypocist velikost ref pool
            self._initRefPool(group.referee_group,100)
        # df zapasy skupiny
        group_matches_df = self.tdo.DfTester._getGroupMatchesDf(group)
        # projdu zapasy skupiny
        for pitch in group_matches_df.columns:
            for match_ind in group_matches_df.index:
                match = group_matches_df.iloc[match_ind,pitch]
                if match:
                    if not match.referee:
                        # zkontrolujeme, zda tym muze piskat
                        for refPool_index in range(len(self.refPool)):
                        # TODO zbytecne prochazime cely pool, stacila by jedna obratka
                            if self.tdo.DfTester._canPlaceTph(self.refPool[refPool_index],match_ind):
                                match.referee = self.refPool.pop(refPool_index)
                                match.save()
                                break

    def _initRefPool(self,referee_group,match_count):
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
