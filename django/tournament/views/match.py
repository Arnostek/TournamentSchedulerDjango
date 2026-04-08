from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from ..models import Match, Group, GroupTieRankingPoints, Schedule


@login_required
def SetScore(request, mid, who, score):
    #print (mid)
    m = Match.objects.get(id = mid)

    if m.locked:
        return HttpResponse("Error: Match locked!", status=400)

    if score > 50:
        return HttpResponse("Error: Score > 50!", status=400)

    if who == 'home':
        m.home_score = score

    elif who == 'away':
        m.away_score = score

    # final match needs winner
    if m.group.NeedsWinner and (m.home_score == m.away_score):
        if who == 'home':
            m.home_score = None
        elif who == 'away':
            m.away_score = None
        return HttpResponse("Error: Match needs winner!", status=400)

    m.save()

    return HttpResponse("OK")


@login_required
def DelScore(request, mid):
    """ Smazani score pro zapas"""
    m = Match.objects.get(id = mid)

    if m.locked:
        return HttpResponse("Error: Match locked!", status=400)

    m.home_score = None
    m.away_score = None
    m.save()

    return HttpResponse("OK")


@login_required
def SwitchMatch(request,  sid1, sid2):
    s1 = Schedule.objects.get(id = sid1)
    s2 = Schedule.objects.get(id = sid2)
    m1 = s1.match
    m2 = s2.match
    s1.match = m2
    s2.match = m1
    s1.save()
    s2.save()
#    t = s1.tournament

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def FinishGroup(request, gid):
    # nacteme skupinu a preklopime poradi do group ranks
    g = Group.objects.get(id = gid)

    if g.finished:
        return HttpResponse("Error: Group already finished!", status=400)

    g.FillRanks()

    return HttpResponse("OK")


@login_required
def ReopenGroup(request, gid):
    # nacteme skupinu a preklopime poradi do group ranks
    g = Group.objects.get(id = gid)

    if not g.finished:
        return HttpResponse("Error: Group is not finished!", status=400)

    g.finished = False
    g.save()

    return HttpResponse("OK")


@login_required
def AddTiePoints(request, gid, tphid):
    # nacteme skupinu
    g = Group.objects.get(id = gid)

    if g.finished:
        return HttpResponse("Error: Group is finished!", status=400)

    if not g.All_scores_filled:
        return HttpResponse("Error: All scores are not filled!", status=400)

    # vytvorime Tie Points
    g.CreateGroupTieRankingPoints()

    # nacteme prislusne group tie points
    gtp = GroupTieRankingPoints.objects.filter(group = g).get(tph__id = tphid)
    gtp.tiepoints += 1
    gtp.save()

    return HttpResponse("OK")
