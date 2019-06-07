from django.urls import path
from . import views
from django.views.decorators.cache import cache_page


cache_timeout = 60 * 2

# unique url patterns
urlpatterns = [
    # score
    path('set/match-<int:mid>/<slug:who>/<int:score>', views.SetScore),
    path('del_score/match-<int:mid>', views.DelScore),
    # move
    path('schedule-move-up-<int:sid>', views.MoveUp),
    path('schedule-move-down-<int:sid>', views.MoveDown),
    # finish group
    path('finish/group-<int:gid>', views.FinishGroup),
]

urlpatterns_tmp = [
    # tournament list
    ('',views.TournamentListView.as_view()),
    # tournament detail
    ('tournament-<int:tid>/', views.TournamentDetailView.as_view()),
    # division system
    ('tournament-<int:tid>/system-division-<int:did>', views.DivisionSystemView.as_view()),
    # division tables
    ('tournament-<int:tid>/tables-division-<int:did>', views.DivisionTablesView.as_view()),
    # schedule
    ('tournament-<int:tid>/schedule-full', views.ScheduleView.as_view()),
    ('tournament-<int:tid>/schedule-division-<int:did>', views.ScheduleView.as_view()),
    ('tournament-<int:tid>/schedule-division-<int:did>-group-<int:gid>', views.ScheduleView.as_view()),
    ('tournament-<int:tid>/schedule-pitch-<int:pid>', views.ScheduleView.as_view()),
    ('tournament-<int:tid>/schedule-team-<int:team>', views.ScheduleView.as_view()),
    
]

# add cached and live version for every url from urlpatterns_tmp
for pat in urlpatterns_tmp:
    urlpatterns.append(path(pat[0], cache_page(cache_timeout)(pat[1])))
    urlpatterns.append(path('live/' + pat[0], pat[1]))
