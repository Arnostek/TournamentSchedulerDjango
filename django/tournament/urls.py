from django.urls import path
from . import views
from django.views.decorators.cache import cache_page


cache_timeout = 60 * 15

urlpatterns = [
    # seznam turnaju
    path('', cache_page(cache_timeout)(views.TournamentListView.as_view())),
    # detail turnaje
    path('tournament-<int:tid>/', cache_page(cache_timeout)(views.TournamentDetailView.as_view())),
    # division system
    path('tournament-<int:tid>/system-division-<int:did>', cache_page(cache_timeout)(views.DivisionSystemView.as_view())),
    # division tables
    path('tournament-<int:tid>/tables-division-<int:did>', cache_page(cache_timeout)(views.DivisionTablesView.as_view())),
    # division tables live
    path('live/tournament-<int:tid>/tables-division-<int:did>', views.DivisionTablesView.as_view()),
    # schedule
    path('tournament-<int:tid>/schedule-full', cache_page(cache_timeout)(views.ScheduleView.as_view())),
    path('tournament-<int:tid>/schedule-division-<int:did>', cache_page(cache_timeout)(views.ScheduleView.as_view())),
    path('tournament-<int:tid>/schedule-division-<int:did>-group-<int:gid>', cache_page(cache_timeout)(views.ScheduleView.as_view())),
    path('tournament-<int:tid>/schedule-pitch-<int:pid>', cache_page(cache_timeout)(views.ScheduleView.as_view())),
    path('tournament-<int:tid>/schedule-team-<int:team>', cache_page(cache_timeout)(views.ScheduleView.as_view())),
    # schedule live
    path('live/tournament-<int:tid>/schedule-full', views.ScheduleView.as_view()),
    path('live/tournament-<int:tid>/schedule-division-<int:did>', views.ScheduleView.as_view()),
    path('live/tournament-<int:tid>/schedule-division-<int:did>-group-<int:gid>', views.ScheduleView.as_view()),
    path('live/tournament-<int:tid>/schedule-pitch-<int:pid>', views.ScheduleView.as_view()),
    path('live/tournament-<int:tid>/schedule-team-<int:team>', views.ScheduleView.as_view()),

    # score
    path('set/match-<int:mid>/<slug:who>/<int:score>', views.SetScore),
    path('del_score/match-<int:mid>', views.DelScore),

    # ukonceni skupiny
    path('finish/group-<int:gid>', views.FinishGroup),
    #path('<int:id>', views.TournamentDetailView.as_view()),
]
