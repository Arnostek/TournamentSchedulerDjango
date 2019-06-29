import pandas as pd

# nacteni schedule do df
[{ 'time' : sch.time, 'pitch' : sch.pitch.name, 'match': sch.match }for sch in Tournament.objects.last().schedule_set.all()]
df = pd.DataFrame([{ 'time' : sch.time, 'pitch' : sch.pitch.name, 'match': sch.match }for sch in Tournament.objects.last().schedule_set.all()])
df = df.pivot(columns='pitch',index='time',values='match')
df


# kontrola dvou zapasu
def has_conflict(m1,m2):
    for tph1 in [m1.home,m1.away,m1.referee]:
        for tph2 in [m2.home,m2.away,m2.referee]:
            if tph1 == tph2:
                print ("Problem match num {} team {}".format(m1,tph1.team.name))

# kontrola vseho
for i in range(36):
    for p1 in range(5):
        for p2 in range(5):
            m1 = df.iloc[i,p1]
            m2 = df.iloc[i+1,p2]
            if m1 and m2:
                has_conflict(m1,m2)
