from django.urls import path
from . import views

urlpatterns = [
    # seznam turnaju
    path('', views.TournamentListView.as_view()),
    # detail turnaje
    path('tournament-<int:tid>/', views.TournamentDetailView.as_view()),
    # division system
    path('tournament-<int:tid>/system/division-<int:did>', views.DivisionSystemView.as_view()),
    # division tables
    path('tournament-<int:tid>/tables/division-<int:did>', views.DivisionTablesView.as_view()),
    # schedule
    path('tournament-<int:tid>/schedule/', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/division-<int:did>', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/division-<int:did>-group-<int:gid>', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/pitch-<int:pid>', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/team-<int:team>', views.ScheduleView.as_view()),

    # score
    path('set/match-<int:mid>/<slug:who>/<int:score>', views.SetScore),
    # ukonceni skupiny
    path('finish/group-<int:gid>', views.FinishGroup),
    #path('<int:id>', views.TournamentDetailView.as_view()),
]
