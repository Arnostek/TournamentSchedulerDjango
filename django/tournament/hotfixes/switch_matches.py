from tournament import models

def get_schedule(game_number):
    return models.Schedule.objects.filter(game_number = game_number)[0]

def  switch_matches(game_number1,game_number2):
    sch1 = get_schedule(game_number1)
    sch2 = get_schedule(game_number2)
    m1 = sch1.match
    m2 = sch2.match
    sch1.match = m2
    sch2.match = m1
    sch1.save()
    sch2.save()
