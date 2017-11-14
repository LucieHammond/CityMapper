## Projet de POOA : Comment y aller ? #

Attention ! Ce projet est codé avec la version 2.7 de python.  
Pour vérifier la version du logiciel que vous utilisez, tapez la commande suivante dans votre console:  
`$ python --version`  
Si python 2.7 n'est pas installé sur votre machine, téléchargez-le à l'adresse https://www.python.org/downloads/

### Etapes à suivre pour installer le projet et lancer l'interface graphique :
1) Téléchargement du projet  
    - *Méthode 1* : Récupérez le dossier .zip envoyé sur Claroline, décompressez-le puis ouvrez un terminal à la racine du projet  
    - *Méthode 2* : Télécharger le projet depuis gitHub et placez vous à la racine avec les commandes suivantes  
  `$ git clone https://github.com/LucieHammond/CityMapper`  
  `$ cd CityMapper`  
  
2) Installation des librairies de dépendance  
    
    Cette étape nécessite le gestionnaire pip. S'il n'est pas déjà installé, vous pouvez soit télécharger get-pip.py (https://bootstrap.pypa.io/get-pip.py), soit exécuter `$ sudo easy_install pip` (Mac et Linux), soit utiliser la commande `$ sudo apt-get install python-pip` (Linux)  
    - *Sur Mac OSX ou Linux* : Lancez le script setUp.sh avec la commande `$ ./setUp.sh`  
    - *Sur Windows* : Exécutez la liste des commandes suivantes dans votre console  
  `$ pip install python-dateutil`  
  `$ pip install requests`

4) Lancement de l'interface graphique  
    - *Sur Mac OSX ou Linux* : Lancez le script run.sh avec la commande `$ ./run.sh`  
    - *Sur Windows* : 
      - Ajoutez le chemin du répertoire CityMapper au pythonpath de votre machine. Pour cela allez dans `My Computer > Properties > Advanced System Settings > Environment Variables` pour Windows XP et 7, ou dans `Start > Settings > System > About > System Info > Advanced System Settings > Environnement variables` pour Windows 10 et modifiez la variable PYTHONPATH (ou Path) en y ajoutant le chemin du répertoire après le signe ;  
      - Exécutez la commande `$ python2.7 gui/home.py`

5) Si vous souhaitez lancer des tests unitaires sur tout le projet, la commande à utiliser est :   
`$ python2.7 -m unittest discover`

### A savoir :
- Le système que nous avons conçu permet à un ou plusieurs utilisateurs de s'enregistrer sur la plateforme pour définir
leurs informations de titres de transports et leurs préférences, puis de s'y reconnecter ultérieurement avec un mot de passe.
Néanmoins, nous n'avons pas implémenté de BDD extérieure permanente pour stocker ces informations.
Ainsi donc, ces données ne seront sauvegardées que temporairement pendant le temps où la fenêtre de l'interface restera ouverte.

- La bibliothèque Tkinter utilisée avec python 2.7 est susceptible de générer un crash de l'application sur Mac OS
lors de la saisie de caractères spéciaux dans un champ de texte. Les caractères à éviter sont ^, \` et ¨.

- L'interface graphique a été conçue pour Mac OSX et a été adaptée à Linux. Il est possible qu'elle soit moins jolie sur Windows
