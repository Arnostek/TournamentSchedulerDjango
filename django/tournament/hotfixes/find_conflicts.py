# Conflict finder
# run following lines:
# docker-compose exec tournament_scheduler python /srv/django/manage.py shell_plus
# from tournament.hotfixes import find_conflicts


import pandas as pd
from tournament.models import Tournament,Schedule
# kontrola dvou zapasu
def has_conflict(m1,m2):
    for tph1 in [m1.home,m1.away,m1.referee]:
        for tph2 in [m2.home,m2.away,m2.referee]:
            if tph1 == tph2:
                if tph1 != None:
                    team_name = tph1
                    if tph1 and tph1.team:
                        team_name = tph1.team.name
                    print ("Problem match num #{} team {}".format(Schedule.objects.get(match=m1).game_number,team_name))

# create schedule dataframe
df = pd.DataFrame([{ 'time' : sch.time, 'pitch' : sch.pitch.name, 'match': sch.match }for sch in Tournament.objects.last().schedule_set.all()])
df = df.pivot(columns='pitch',index='time',values='match')

# check all
for i in range(len(df)-1):
    for p1 in range(len(df.columns)):
        for p2 in range(len(df.columns)):
            m1 = df.iloc[i,p1]
            m2 = df.iloc[i+1,p2]
            if m1 and m2:
                has_conflict(m1,m2)
