## Projet de POOA : Comment y aller ? #

Attention ! Ce projet est codé avec la version 2.7 de python.  
Pour vérifier la version du logiciel que vous utilisez, tapez la commande suivante dans votre console:  
`$ python --version`  
Si python 2.7 n'est pas installé sur votre machine, allez le télécharger à l'adresse https://www.python.org/downloads/

#### Etapes à suivre pour installer le projet et lancer l'interface graphique :
1) Téléchargez le projet sur votre machine en décompressant le fichier zip envoyé  
2) Ouvrez un terminal à la racine du projet  
Remarque : Vous pouvez également télécharger le projet depuis git avec les commandes  
`$ git clone https://github.com/LucieHammond/CityMapper`  
`$ cd CityMapper`  
3) Pour installer les librairies de dépendance, lancez le script setUp.sh  
`$ ./setUp.sh`
4) Pour lancer l'interface graphique, utilisez le script run.sh  
`$ ./run.sh`
5) Pour lancer les tests unitaires sur tout le projet, vous pouvez exécuter la commande suivante :   
`$ python2.7 -m unittest discover`

#### A savoir :
- Le système que nous avons conçu permet à un ou plusieurs utilisateurs de s'enregistrer sur la plateforme pour définir
leurs informations de titres de transports et leurs préférences, puis de s'y reconnecter ultrieurement avec un mot de passe.
Néanmoins, nous n'avons pas implémenté de BDD extérieure permanente pour stocker ces informations.
Ainsi donc, ces données ne seront sauvegardées que temporairement pendant le temps où la fenêtre de l'interface restera ouverte.

- La bibliothèque Tkinter utilisée avec python 2.7 est susceptible de générer un crash de l'application sur Mac OS
lors de la saisie de caractères spéciaux dans un champ de texte. Les caractères à éviter sont ^, \` et ¨.

- L'interface graphique a été conçue pour Mac OSX et a été adaptée à Linux. Il est possible qu'elle soit moins jolie sur Windows
