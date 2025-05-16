from django.urls import path
from . import views
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.http import HttpRequest
from functools import wraps

# Cache timeout (e.g., 2 minutes)
cache_timeout = 60 * 2

# Custom decorator to skip caching for admin users
def cache_exclude_admin(timeout):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            # Skip caching if user is admin
            if request.user.is_authenticated and request.user.is_staff:
                return view_func(request, *args, **kwargs)
            return cache_page(timeout)(view_func)(request, *args, **kwargs)
        return wrapper
    return decorator

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
    path('add-tiepoints/group-<int:gid>-tph-<int:tphid>', views.AddTiePoints),
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
    # conflicts
    ('<slug:slug>/conflicts', views.ConflictsView.as_view()),
        # tv
    ('<slug:slug>/tv', views.TVView.as_view()),
]

# add cached and live version for every url from urlpatterns_tmp
for pat in urlpatterns_tmp:
    urlpatterns.append(path(pat[0], cache_exclude_admin(cache_timeout)(pat[1])))
    urlpatterns.append(path('live/' + pat[0], pat[1]))
