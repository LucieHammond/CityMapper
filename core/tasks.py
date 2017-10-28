# -*- coding: utf-8 -*-

from threading import Thread
from Queue import Queue


class Worker(Thread):
    """ Thread qui permet d'accomplir une tâche en asynchrone avec une réponse récupérable """

    def __init__(self, target, args):
        Thread.__init__(self)
        self._target = target  # function cible à exécuter en asynchrone
        self._args = args  # paramêtres de la fonction cible
        self._return = None  # réponse renvoyée

    def run(self):
        self._return = self._target(*self._args)

    def get_result(self):
        """ Attend la fin du thread et renvoie le résultat de la fonction cible

        Si la tache n'est pas finie au bout de 10 secondes, on la force à se terminer et on lance une erreur Timeout
        C'est probablement un problème de connection à l'API (pas de réseau)

        """
        self.join(10)
        if self.isAlive():
            raise TimeoutError
        if isinstance(self._return, Exception):
            raise self._return
        return self._return


class TasksManager(object):
    """ Gestionnaire de tâches assynchrones multiples et successives """

    def __init__(self, queue=None):
        # Les Workers lancés sont stockés dans une queue
        self._queue = queue if queue else Queue()

    @property
    def queue(self):
        return self._queue

    def new_task(self, target, args=()):
        """ Crée et démarre un nouveau Worker (Thread avec retour) que l'on ajoute à la queue """
        thread = Worker(target=target, args=args)
        thread.start()
        self._queue.put(thread)

    def next_result(self):
        """ Met fin au premier Worker en attente et renvoie son résultat """
        return self._queue.get().get_result()

    def results_list(self):
        """
            Met fin à tous les Workers dans l'ordre dans lequel ils ont commencé
            Récupère leurs résultats dans une liste ordonnée et renvoie la liste
        """
        results = list()
        while not self._queue.empty():
            results.append(self._queue.get().get_result())
        return results


class TimeoutError(RuntimeError):

    def __str__(self):
        return "L'API ne répond pas, vérifiez votre connexion à Internet"