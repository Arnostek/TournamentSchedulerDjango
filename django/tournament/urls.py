from django.urls import path
from . import views

urlpatterns = [
    path('', views.TournamentListView.as_view()),
    path('tournament/<int:id>', views.TournamentDetailView.as_view()),
    path('tournament/system/<int:id>', views.DivisionSystemView.as_view()),
    #path('<int:id>', views.TournamentDetailView.as_view()),
]
