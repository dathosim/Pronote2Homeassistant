import pronotepy
import os
from datetime import date
from datetime import timedelta 
import json


#Variables
eleve="demo"
prefix_url = "demo"
username="demonstration"
password="pronotevs"

#Connection à Pronote 
client = pronotepy.Client('https://'+prefix_url+'.index-education.net/pronote/eleve.html?login=true', username, password)

#Si on est bien connecté
if client.logged_in:
    
    #Récupération  emploi du temps du jour
    lessons_today = client.lessons(date.today())
    lessons_today = sorted(lessons_today, key=lambda lesson: lesson.start)

    #Récupération  emploi du lendemain
    lessons_tomorrow = client.lessons(date.today()+ timedelta(days = 1))
    lessons_tomorrow = sorted(lessons_tomorrow, key=lambda lesson: lesson.start)
    delta = 1

    #Récupération  emploi du prochain jour d'école (ça sert le weekend et les vacances)
    lessons_nextday = client.lessons(date.today()+ timedelta(days = delta))
    while not lessons_nextday:
        lessons_nextday = client.lessons(date.today()+ timedelta(days = delta))
        delta = delta + 1 
    lessons_nextday = sorted(lessons_nextday, key=lambda lesson: lesson.start)

    #Transformation Json des emplois du temps (J,J+1 et next)
    jsondata = {}
    jsondata['edt_aujourdhui'] = []
    for lesson in lessons_today:
        jsondata['edt_aujourdhui'].append({
            'id': lesson.id,
            'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
            'date': lesson.start.strftime("%d/%m/%Y"),
            'heure': lesson.start.strftime("%H:%M"),
            'heure_fin': lesson.end.strftime("%H:%M"),
            'cours': lesson.subject.name,
            'salle': lesson.classroom,
            'annulation': lesson.canceled,
            'status': lesson.status,
            'background_color': lesson.background_color,
    })
    jsondata['edt_demain'] = []
    for lesson in lessons_tomorrow:
        jsondata['edt_demain'].append({
            'id': lesson.id,            
            'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
            'date': lesson.start.strftime("%d/%m/%Y"),
            'heure': lesson.start.strftime("%H:%M"),
            'heure_fin': lesson.end.strftime("%H:%M"),            
            'cours': lesson.subject.name,
            'salle': lesson.classroom,
            'annulation': lesson.canceled,
            'status': lesson.status,
            'background_color': lesson.background_color,
    })

    jsondata['edt_prochainjour'] = []
    for lesson in lessons_nextday:
        jsondata['edt_prochainjour'].append({
            'id': lesson.id,            
            'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
            'date': lesson.start.strftime("%d/%m/%Y"),
            'heure': lesson.start.strftime("%H:%M"),
            'heure_fin': lesson.end.strftime("%H:%M"),            
            'cours': lesson.subject.name,
            'salle': lesson.classroom,
            'annulation': lesson.canceled,
            'status': lesson.status,
            'background_color': lesson.background_color,
    })

    #Stockage dans un fichier json 
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, "../www/pronote_edt_"+eleve+".json"), "a") as outfile:
        outfile.truncate(0)
        json.dump(jsondata, outfile, indent=4)




    
 