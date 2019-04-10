from django.urls import path
from . import views

urlpatterns = [
    path('', views.TournamentListView.as_view()),
    path('tournament-<int:tid>/', views.TournamentDetailView.as_view()),
    # division system
    path('tournament-<int:tid>/division-<int:did>/system', views.DivisionSystemView.as_view()),
    # schedule
    path('tournament-<int:tid>/schedule/', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/division-<int:did>', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/division-<int:did>-group-<int:gid>', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/pitch-<int:pid>', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/team-<int:team>', views.ScheduleView.as_view()),

    # score
    path('set/match-<int:mid>/<slug:who>/<int:score>', views.SetScore),
    #path('<int:id>', views.TournamentDetailView.as_view()),
]
