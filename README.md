# Pronote2Homeassistant
Tuto et bout de code pour ajouter des éléments de Pronote dans Home assistant

1. Installation des scripts Python

Installer le script python pronote_edt.py et le faire tourner sur le serveur HA
Personnelement, je le fais tourner dans un dossier /python_scripts/ sous le /config de HA 

Il génère un fichier pronote_edt_eleve.json qu'il dépose dans /config/www/

2. Configuration YAML pour récupérer l'emploi du temps dans un sensor

Copier/coller le fichier configuration.yaml fourni dans ce repo dans votre configuration HA 
N'oubliez pas de mettre la bonne adresse IP interne de votre HA (ne pas laisser 192.168.XX.XX)



