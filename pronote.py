from ast import If
import pronotepy
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

#Variables a remplacer (ou laisser comme ça pour tester la démo)
eleve_id="demo" #prénom de votre enfant par exemple - ne sert que pour le nom du fichier json - pas d'espace - pas d'accent !! 
eleve_nom_prenom = "PARENT Fanny" #NOM Prénom de votre enfant - sert quand on se connecte avec un compte parent qui a plusieurs enfants !
prefix_url = "demo" # sert au prefix de l'url https://PREFIX.index-education.net/pronote/
type_compte = "eleve" #eleve ou parent - si vous utlisez un compte parent ou eleve pour vous connecter 
username="demonstration" #utlisateur pronote  - a remplacer par le nom d'utilisateur pronote de l'élève ou du parent si type_compte=parent
password="pronotevs" # mot de passe pronote - a remplacer par le mot de passe du compte de l'élève ou du parent si type_compte=parent
ent = None #A initialiser si connexion via ENT - avec le nom technique de l'ENT - exemple : ent=paris_classe_numerique


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
    for lesson in lessons_today:
        index=lessons_today.index(lesson)
        if not (lesson.start == lessons_today[index-1].start and lesson.canceled == True) :        
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
        index=lessons_tomorrow.index(lesson)
        if not (lesson.start == lessons_tomorrow[index-1].start and lesson.canceled == True) :
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
        index=lessons_nextday.index(lesson)
        if not (lesson.start == lessons_nextday[index-1].start and lesson.canceled == True) :
            jsondata['edt_prochainjour'].append({
                'index': index,            
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
    #print(json.dumps(jsondata['edt_prochainjour'], indent=4))

    jsondata['edt_date'] = []
    for lesson in lessons_specific:
        index=lessons_specific.index(lesson)
        if not (lesson.start == lessons_specific[index-1].start and lesson.canceled == True) :
            jsondata['edt_date'].append({
                'index': index,            
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
    absences = client.current_period.absences()
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

    
    print(json.dumps(jsondata['evaluation'], indent=4))



    #Stockage dans un fichier json : edt + notes + devoirs 
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(location, "../www/pronote_"+eleve_id+".json"), "a") as outfile:
        outfile.truncate(0)
        json.dump(jsondata, outfile, indent=4)
    
