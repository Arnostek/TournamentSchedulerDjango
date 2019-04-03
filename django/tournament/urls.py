from django.urls import path
from . import views

urlpatterns = [
    path('', views.TournamentListView.as_view()),
    path('tournament-<int:tid>/', views.TournamentDetailView.as_view()),
    path('tournament-<int:tid>/division-<int:did>/system', views.DivisionSystemView.as_view()),
    path('tournament-<int:tid>/schedule/', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/division-<int:did>', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/pitch-<int:pid>', views.ScheduleView.as_view()),
    path('tournament-<int:tid>/schedule/team-<int:team>', views.ScheduleView.as_view()),
    path('set/match-<int:mid>', views.SetScore),
    #path('<int:id>', views.TournamentDetailView.as_view()),
]
