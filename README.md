## Projet de POOA : Comment y aller ? #

Attention ! Ce projet est codé avec la version 2.7 de python.  
Pour vérifier la version de python que vous utilisez, tapez la commande suivante dans votre console:  
`$ python --version`  
Si python 2.7 n'est pas installé sur votre machine, allez le télécharger à l'adresse https://www.python.org/downloads/

Etapes à suivre pour lancer l'interface graphique :
- Téléchargez le projet entier sur votre machine  
    x soit à partir du zip envoyé et décompressé  
    x soit directement depuis git avec la commande `$ git clone https://github.com/LucieHammond/CityMapper`
- Ouvrez un terminal à la racine du projet
- Tapez les commandes suivantes :  
    `$ export PYTHONPATH=$PYTHONPATH:'pwd'`  
    `$ python2.7 gui/home.py`

Pour lancer les tests unitaires sur tout le projet, vous pouvez lancer la commande suivante :  
`$ python2.7 -m unittest discover`

Remarques :
1) Le système que nous avons conçu permet à un ou plusieurs utilisateurs de s'enregistrer sur la plateforme pour définir
leurs informations de titres de transports et leurs préférences, puis de s'y reconecter ultrieurement avec un mot de passe.
Néanmoins, nous n'avons pas implémenté de BDD extérieure permanente pour stocker ces utilisateurs.
Ainsi donc, ces données ne seront stockées que temporairement pendant le temps où la fenêtre de l'interface restera ouverte.

2) La bibliothèque Tkinter utilisée avec python 2.7 est susceptible de générer un crash de l'application sur Mac OS
lors de la saisie de caractères spéciaux dans un champ de texte. Les caractères à éviter sur mac sont donc ^, ` et ¨.
