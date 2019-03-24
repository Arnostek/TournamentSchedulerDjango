from django.urls import path
from . import views

urlpatterns = [
    path('', views.TournamentListView.as_view()),
    path('tournament/<int:id>', views.TournamentDetailView.as_view()),
]
