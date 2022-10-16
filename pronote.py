from ast import If
import pronotepy
from pronotepy.dataClasses import Lesson
from pronotepy.ent import ac_lyon
from pronotepy.ent import ac_grenoble
from pronotepy.ent import ac_orleans_tours
from pronotepy.ent import ac_reims
from pronotepy.ent import ac_reunion
from pronotepy.ent import atrium_sud
from pronotepy.ent import ile_de_france
from pronotepy.ent import monbureaunumerique
from pronotepy.ent import occitanie_montpellier
from pronotepy.ent import paris_classe_numerique

import os
import sys
from datetime import date
from datetime import timedelta 
import json
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
section="defaut"
if len(sys.argv) > 1:
    section = sys.argv[1]


eleve_id = config.get(section, "eleve_id")
eleve_nom_prenom = config.get(section, "eleve_nom_prenom")
prefix_url = config.get(section, "prefix_url")
type_compte = config.get(section, "type_compte")
username = config.get(section, "username")
password = config.get(section, "password")
ent = config.get(section, "ent")

if ent == "ac_lyon":
        ent = ac_lyon
elif ent == "ac_grenoble":
        ent = ac_grenoble
elif ent == "ac_orleans_tours":
        ent = ac_orleans_tours
elif ent == "ac_reims":
        ent = ac_reims
elif ent == "ac_reunion":
        ent = ac_reunion
elif ent == "atrium_sud":
        ent = atrium_sud
elif ent == "ile_de_france":
        ent = ile_de_france
elif ent == "monbureaunumerique":
        ent = monbureaunumerique
elif ent == "occitanie_montpellier":
        ent = occitanie_montpellier
elif ent == "paris_classe_numerique":
        ent = paris_classe_numerique
else:
        ent = None

#Autres de configuration
index_note=0 #debut de la boucle des notes
limit_note=11 #nombre max de note à afficher + 1 
longmax_devoir = 125 #nombre de caractère max dans la description des devoirs



#Connection à Pronote avec ou sans ENT
if ent:
    if type_compte == "parent":
        try:
            client = pronotepy.ParentClient('https://'+prefix_url+'.index-education.net/pronote/parent.html', username, password, ent)
        except:
            print("Erreur de connexion via l'ENT avec le compte parent - vérifier les paramètres")
    else:
        try:
            client = pronotepy.Client('https://'+prefix_url+'.index-education.net/pronote/eleve.html', username, password, ent)
        except:
            print("Erreur de connexion via l'ENT avec le compte eleve - vérifier les paramètres")
else:
    if type_compte == "parent":
        try:
            client = pronotepy.ParentClient('https://'+prefix_url+'.index-education.net/pronote/parent.html?login=true', username, password)
        except:
            print("Erreur de connexion à Pronote (sans ENT) avec le compte parent - vérifier les paramètres")
    else:
        try:
            client = pronotepy.Client('https://'+prefix_url+'.index-education.net/pronote/eleve.html?login=true', username, password)
        except:
            print("Erreur de connexion à Pronote (sans ENT) avec le compte élève - vérifier les paramètres")

#Si on est bien connecté
if client.logged_in:
    if type_compte == "parent":
        client.set_child(eleve_nom_prenom)

    #Récupération du nom, de la classe et de l'établissement et stockage dans le json
    jsondata = {}
    jsondata['identite'] = []
    jsondata['identite'].append({
        'nom_complet': client.info.name,   
        'classe': client.info.class_name,
        'etablissement': client.info.establishment,
    })
#    print(json.dumps(jsondata['identite'], indent=4))


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

    #Récupération  emploi d'un jour spécifique pour des tests
    lessons_specific = client.lessons(date(2022, 2, 14))
    lessons_specific = sorted(lessons_specific, key=lambda lesson: lesson.start)

    #Transformation Json des emplois du temps (J,J+1 et next)
    jsondata['edt_aujourdhui'] = []
    jsondata['edt_aujourdhui_debut'] = ""

    for lesson in lessons_today:
        index=lessons_today.index(lesson)
        if not (lesson.start == lessons_today[index-1].start and lesson.canceled == True) :                    
            if lesson.subject: cours_affiche = lesson.subject.name
            else: cours_affiche = 'autre'
            if lesson.detention == True: cours_affiche = 'RETENUE'
            jsondata['edt_aujourdhui'].append({
                'id': lesson.id,
                'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
                'date': lesson.start.strftime("%d/%m/%Y"),
                'heure': lesson.start.strftime("%H:%M"),
                'heure_fin': lesson.end.strftime("%H:%M"),
                'cours': cours_affiche,
                'salle': lesson.classroom,
                'annulation': lesson.canceled,
                'status': lesson.status,
                'background_color': lesson.background_color,
            })
        if lesson.canceled == False and jsondata['edt_aujourdhui_debut'] == '' :
            jsondata['edt_aujourdhui_debut'] = lesson.start.strftime("%H:%M")



    jsondata['edt_demain'] = []
    jsondata['edt_demain_debut'] = ""

    for lesson in lessons_tomorrow:

        index=lessons_tomorrow.index(lesson)
        if not (lesson.start == lessons_tomorrow[index-1].start and lesson.canceled == True) :
            if lesson.subject: cours_affiche = lesson.subject.name
            else: cours_affiche = 'autre'
            if lesson.detention == True: cours_affiche = 'RETENUE'
            jsondata['edt_demain'].append({
                'id': lesson.id,            
                'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
                'date': lesson.start.strftime("%d/%m/%Y"),
                'heure': lesson.start.strftime("%H:%M"),
                'heure_fin': lesson.end.strftime("%H:%M"),            
                'cours': cours_affiche,
                'salle': lesson.classroom,
                'annulation': lesson.canceled,
                'status': lesson.status,
                'background_color': lesson.background_color,
            })
        if lesson.canceled == False and jsondata['edt_demain_debut'] == '' :
            jsondata['edt_demain_debut'] = lesson.start.strftime("%H:%M")            

    jsondata['edt_prochainjour'] = []
    jsondata['edt_prochainjour_debut'] = ""
    for lesson in lessons_nextday:
        index=lessons_nextday.index(lesson)
        if not (lesson.start == lessons_nextday[index-1].start and lesson.canceled == True) :
            if lesson.subject: cours_affiche = lesson.subject.name
            else: cours_affiche = 'autre'
            if lesson.detention == True: cours_affiche = 'RETENUE'
            jsondata['edt_prochainjour'].append({
                'index': index,            
                'id': lesson.id,            
                'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
                'date': lesson.start.strftime("%d/%m/%Y"),
                'heure': lesson.start.strftime("%H:%M"),
                'heure_fin': lesson.end.strftime("%H:%M"),            
                'cours': cours_affiche,
                'salle': lesson.classroom,
                'annulation': lesson.canceled,
                'status': lesson.status,
                'background_color': lesson.background_color,
        })
        if lesson.canceled == False and jsondata['edt_prochainjour_debut'] == '' :
            jsondata['edt_prochainjour_debut'] = lesson.start.strftime("%H:%M")
            #print(json.dumps(jsondata['edt_prochainjour'], indent=4))


    jsondata['edt_date'] = []
    for lesson in lessons_specific:
        index=lessons_specific.index(lesson)
        if  (lesson.start == lessons_specific[index-1].start) :
            lesson.num
        else: 
            if lesson.subject: cours_affiche = lesson.subject.name
            else: cours_affiche = 'autre'
            if lesson.detention == True: cours_affiche = 'RETENUE'
            jsondata['edt_date'].append({
                'index': index,            
                'id': lesson.id,            
                'date_heure': lesson.start.strftime("%d/%m/%Y, %H:%M"),
                'date': lesson.start.strftime("%d/%m/%Y"),
                'heure': lesson.start.strftime("%H:%M"),
                'heure_fin': lesson.end.strftime("%H:%M"),            
                'cours': cours_affiche,
                'salle': lesson.classroom,
                'annulation': lesson.canceled,
                'status': lesson.status,
                'num': lesson.num,
                'background_color': lesson.background_color,
    })

    #Récupération des notes 
    grades = client.current_period.grades
    grades = sorted(grades, key=lambda grade: grade.date, reverse=True)

    #Transformation des notes en Json
    jsondata['note'] = []
    for grade in grades:
        index_note += 1
        if index_note == limit_note:
            break
        jsondata['note'].append({
            'date': grade.date.strftime("%d/%m/%Y"),
            'date_courte': grade.date.strftime("%d/%m"),            
            'cours': grade.subject.name,
            'note': grade.grade,            
            'sur': grade.out_of,
            'note_sur': grade.grade+'\u00A0/\u00A0'+grade.out_of,
            'coeff': grade.coefficient,
            'moyenne_classe': grade.average,           
            'max': grade.max,
            'min': grade.min,

    })

    #Récupération des devoirs
    homework_today = client.homework(date.today())
    homework_today = sorted(homework_today, key=lambda lesson: lesson.date)
    jsondata['devoir'] = []

    #Transformation des devoirs  en Json   
    for homework in homework_today:
        jsondata['devoir'].append({
            'index': homework_today.index(homework),
            'date': homework.date.strftime("%d/%m"),
            'title': homework.subject.name,
            'description': (homework.description)[0:longmax_devoir],
            'description_longue': (homework.description),
            'done' : homework.done,            
    })

    #Récupération  des absences pour l'année
    #absences = [period.absences for period in client.periods]
    #Récupération  des absences pour la période en cours 
    absences = client.current_period.absences
    absences = sorted(absences, key=lambda absence: absence.from_date, reverse=True)



    #Transformation des absences en Json
    jsondata['absence'] = []
    #for period in absences:
    #    for absence in period():
    for absence in absences:    
            jsondata['absence'].append({            
                'id': absence.id,
                'date_debut': absence.from_date.strftime("%d/%m/%y %H:%M"),
                'date_debut_format': absence.from_date.strftime("Le %d %b à %H:%M"),
                'date_fin': absence.to_date.strftime("%d/%m/%y %H:%M"),
                'justifie': absence.justified,
                'nb_heures': absence.hours,
                'nb_jours': absence.days,
                'raison': str(absence.reasons)[2:-2],        
            })

#    print(json.dumps(jsondata['absence'], indent=4))


    #Récupération des evaluations
    evaluations = client.current_period.evaluations
    evaluations = sorted(evaluations, key=lambda evaluation: (evaluation.subject.name, evaluation.date))


    #Transformation des evaluations en Json
    jsondata['evaluation'] = []
    for evaluation in evaluations:
        jsondata['evaluation'].append({
            'date': evaluation.date.strftime("%d/%m/%Y"),
            'date_courte': evaluation.date.strftime("%d/%m"),            
            'eval': evaluation.subject.name,
            'desc': evaluation.description,            
            'coeff': evaluation.coefficient,
            'palier': evaluation.paliers,
            'prof': evaluation.teacher,
        })
        jsondata['acquisition'] = []
        for acquisition in evaluation.acquisitions:
            jsondata['acquisition'].append({
                'acquisition_ordre': acquisition.order,
                'acquisition': acquisition.name,
                'acquisition_niveau': acquisition.abbreviation,
                'acquisition_niveau_info': acquisition.level,
                'acquisition_domaine': acquisition.domain,
            })      
        jsondata['evaluation'].append(jsondata['acquisition'])        

    
    #print(json.dumps(jsondata['evaluation'], indent=4))



    #Stockage dans un fichier json : edt + notes + devoirs 
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(location, "../www/pronote_"+eleve_id+".json"), "a") as outfile:
        outfile.truncate(0)
        json.dump(jsondata, outfile, indent=4)
    
