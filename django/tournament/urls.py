from django.urls import path
from . import views
from django.views.decorators.cache import cache_page


cache_timeout = 60 * 2

# unique url patterns
urlpatterns = [
    # score
    path('set/match-<int:mid>/<slug:who>/<int:score>', views.SetScore),
    path('del_score/match-<int:mid>', views.DelScore),
    # switch match
    path('schedule-switch-<int:sid1>-<int:sid2>', views.SwitchMatch),
    # finish group
    path('finish/group-<int:gid>', views.FinishGroup),
    path('reopen/group-<int:gid>', views.ReopenGroup),
    # Check for conflicts
    path('findconflicts/tournament-<int:tid>', views.FindConflicts),
    path('<slug:slug>/findconflicts', views.FindConflicts),
    path('live/<slug:slug>/findconflicts', views.FindConflicts),
]

urlpatterns_tmp = [
    # tournament list
    ('',views.TournamentListView.as_view()),
    # tournament detail
    ('<slug:slug>/', views.TournamentDetailView.as_view()),
    # division system
    ('<slug:slug>/system-division-<int:did>', views.DivisionSystemView.as_view()),
    # division tables
    ('<slug:slug>/tables-division-<int:did>', views.DivisionTablesView.as_view()),
    ('<slug:slug>/crosstables-division-<int:did>', views.DivisionCrossTablesView.as_view()),
    # schedule
    ('<slug:slug>/schedule-full', views.ScheduleView.as_view()),
    ('<slug:slug>/schedule-division-<int:did>', views.ScheduleView.as_view()),
    ('<slug:slug>/schedule-division-<int:did>-group-<int:gid>', views.ScheduleView.as_view()),
    ('<slug:slug>/schedule-pitch-<int:pid>', views.ScheduleView.as_view()),
    ('<slug:slug>/schedule-team-<int:team>', views.ScheduleView.as_view()),
    # protocols
    ('<slug:slug>/protocols-pitch-<int:pid>', views.ProtocolsView.as_view()),
    ('<slug:slug>/protocols-group-<int:gid>', views.ProtocolsView.as_view()),
    ('<slug:slug>/protocols-division-<int:did>-phase-<int:phase>', views.ProtocolsView.as_view()),
    #ranking
    ('<slug:slug>/ranking-division-<int:did>', views.DivisionRankingView.as_view()),
    ('<slug:slug>/ranking-all', views.DivisionRankingView.as_view()),
    # prints
    ('<slug:slug>/prints', views.PrintsView.as_view()),
]

# add cached and live version for every url from urlpatterns_tmp
for pat in urlpatterns_tmp:
    urlpatterns.append(path(pat[0], cache_page(cache_timeout)(pat[1])))
    urlpatterns.append(path('live/' + pat[0], pat[1]))
