from django.urls import path
from . import views

urlpatterns = [
    path('', views.TournamentListView.as_view()),
    path('tournament-<int:tid>/', views.TournamentDetailView.as_view()),
    path('tournament-<int:tid>/division-<int:did>/system', views.DivisionSystemView.as_view()),
    path('tournament-<int:tid>/schedule', views.ScheduleView.as_view()),
    #path('<int:id>', views.TournamentDetailView.as_view()),
]
