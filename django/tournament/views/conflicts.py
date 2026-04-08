from django.views.generic import TemplateView
from ..models import Tournament
import pandas as pd


class ConflictsView(TemplateView):
    template_name = 'conflicts.html'

    def get_context_data(self, **kwargs):
        # nacteme Tournament
        tm = Tournament.objects.get(slug = self.kwargs['slug'])
        # conflicts
        conflicts = []
        # nacteni schedule do dataframe
        df = pd.DataFrame([{ 'time' : sch.time, 'pitch' : sch.pitch.name, 'match': sch.match }for sch in tm.schedule_set.all()])
        df = df.pivot(columns='pitch',index='time',values='match')
        # projdeme radky
        for i in range(len(df)-1):
            # projdeme hriste
            for p1 in range(len(df.columns)):
                m1 = df.iloc[i,p1]
                # chybejici rozhodci
                if m1 and not m1.referee:
                    conflicts.append({
                        "problem":"Missing referee",
                        "division":m1.division,
                        "group":m1.group,
                        "match":m1,
                        "schedule":m1.schedule_set.last(),
                        })
                # druhy zapas kontrolujeme na vsech hristich
                for p2 in range(len(df.columns)):
                    # stejny a nasledujici cas
                    for m2 in [df.iloc[i,p2],df.iloc[i+1,p2]]:
                        if m1 and m2 and m1 != m2:
                            for typ1,tph1 in [("play",m1.home),("play",m1.away),("ref",m1.referee)]:
                                for typ2,tph2 in [("play",m2.home),("play",m2.away),("ref",m2.referee)]:
                                    if tph1 == tph2 and tph1 != None:
                                        conflicts.append({
                                            "problem":"Team conflict - " + typ1 + " " + typ2,
                                            "division":m1.division,
                                            "group":m1.group,
                                            "match":m1,
                                            "schedule":m1.schedule_set.last(),
                                            "team":tph1,
                                            "match2":m2,
                                            })
        # data pro sablonu
        return {'conflicts':conflicts}
