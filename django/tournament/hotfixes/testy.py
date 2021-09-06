from tournament.TournamentScheduler import TournamentScheduler,TournamentSchedulerDataframeCreator
ts = TournamentScheduler(Tournament.objects.all().last(),3)
tdc = TournamentSchedulerDataframeCreator(Tournament.objects.last())
