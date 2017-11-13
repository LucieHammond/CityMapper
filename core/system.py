# -*- coding: utf-8 -*-

from user import User
from ride import Ride
from datetime import date
import re
from webservice.api_manager import ApiCallError, ParamNotFoundError
from webservice.geocode import Geocode, ZeroResultsError
from tasks import TasksManager, TimeoutError


# Vérifie le type des arguments des fonctions du système
def check_params(*types):
    def params_accepts(funct):
        def new_function(*args, **kwargs):
            for (a, t) in zip(args, types):
                assert isinstance(a, t)
            return funct(*args, **kwargs)

        return new_function
    return params_accepts


# Affiche et renvoie dans un format standard l'erreur dont le message est passé en paramètre
def format_error(message):
    print message
    return {"success": False, "error": message}


class HowToGoSystem(object):
    """ Interface du système de calcul d'itinéraire 'Comment y aller' qui couvre toutes ses fonctionnalités
        Seules les méthodes définies ici pourront être appelées par l'interface graphique """

    def __init__(self):
        self._users = list()
        self._current_user = None  # Utilisateur connecté au système
        self._current_ride = None  # Trajet sauvegardé, pour lequel on calcule les meilleurs itinéraires

    @property
    def current_user(self):
        return self._current_user

    @property
    def current_ride(self):
        return self._current_ride

    @check_params(object, basestring, basestring, date)
    def sign_up(self, username, password, birthdate):
        """
        Inscription d'un nouvel utilisateur dans le système
        :param username: nom d'utilisateur (string)
        :param password: mot de passe (string)
        :param birthdate: date de naissance (date)
        :return: {'success': Bool, ('error': 'message d'erreur' si success = False) }
        """
        for user in self._users:
            if user.username == username:
                return format_error("Désolé, le nom d'utilisateur '%s' n'est pas disponible" % username)
        try:
            new_user = User(username, password, birthdate)
        except ValueError as e:
            return format_error(e.message)
        else:
            self._current_user = new_user
            self._users.append(new_user)
            return {"success": True}

    @check_params(object, basestring, basestring)
    def sign_in(self, username, password):
        """
        Connexion au système d'un utilisateur déjà enregistré
        :param username: nom d'utilisateur (string)
        :param password: mot de passe (string)
        :return: {'success': Bool, ('error': 'message d'erreur' si success = False) }
        """
        for user in self._users:
            if user.username == username and user.password == password:
                self._current_user = user
                return {"success": True}
        return format_error("Le nom d'utilisateur ou le mot de passe est incorrect")

    @check_params(object)
    def sign_out(self):
        """
        Déconnexion de l'utilisateur actuellement connecté
        :return:  {'success': Bool, ('error': 'message d'erreur' si success = False) }
        """
        if self._current_user:
            self._current_user = None
            self._current_ride = None
            return {"success": True}
        else:
            return format_error("Aucun utilisateur n'est actuellement connecté")

    @check_params(object, basestring, basestring, basestring, bool, dict)
    def set_profile_settings(self, velib, autolib, subway, driving_licence, preferences):
        """
        Définition ou modification du profil utilisateur
        :param velib: titre de transport pour vélib (string parmi la liste des possibles)
        :param autolib: titre de transport pour autolib (string parmi la liste des possibles)
        :param subway: titre de transport pour RATP (métro/RER/bus...) (string parmi la liste des possibles)
        :param driving_licence: permis de conduire (bool)
        :param preferences: préférences pour les critères d'optimisation des trajets (dict)
        :return: {'success': Bool, ('error': 'message d'erreur' si success = False) }
        """
        if self._current_user:
            try:
                self._current_user.set_subscriptions_infos(velib, autolib, subway)
                self._current_user.driving_licence = driving_licence
                self._current_user.preferences = preferences
                return {"success": True}
            except ValueError:
                return format_error("L'un des paramètres renseignés a une valeur inattendue")
        else:
            return format_error("Aucun utilisateur n'est actuellement connecté")

    @check_params(object, basestring, basestring, float)
    def new_ride(self, start_address, end_address, departure_time):
        """
        Créer et sauvegarder un nouveau trajet
        :param start_address: adresse de départ (string)
        :param end_address: adresse d'arrivée (string)
        :param departure_time: moment du départ (timestamp)
        :return: {'success': Bool, ('error': 'message d'erreur' si success = False) }
        """
        if self._current_user:
            start, end = None, None

            # Si l'adresse est déjà renseignée en temps que coordonnées sous la forme "@ longitude,latitude"
            re_start = re.match('^@ (\d+.\d+), ?(\d+.\d+)$', start_address)
            if re_start:
                start = (float(re_start.group(1)), float(re_start.group(2)))
            re_end = re.match('^@ (\d+.\d+), ?(\d+.\d+)$', end_address)
            if re_end:
                end = (float(re_end.group(1)), float(re_end.group(2)))

            # Convertir l'adresse en coordonnées géographiques
            try:
                geocode = Geocode()
                tm = TasksManager()
                if not start:
                    tm.new_task(target=geocode.get_from_api, args=(start_address,))
                if not end:
                    tm.new_task(target=geocode.get_from_api, args=(end_address,))
                if not start:
                    start = tm.next_result()
                if not end:
                    end = tm.next_result()

            except TimeoutError as e:
                return format_error(e)
            except ApiCallError as e:
                return format_error("Géocode: " + str(e))
            except ZeroResultsError as e:
                return format_error(e)
            except ParamNotFoundError as e:
                return format_error("Géocode: " + str(e))

            # Créer un nouveau ride (météo demandée au moment de la création)
            try:
                new_ride = Ride(self._current_user, start, end, departure_time)
            except TimeoutError as e:
                return format_error(e)
            except ApiCallError as e:
                return format_error("WeatherMap :" + str(e))
            except ParamNotFoundError as e:
                return format_error("WeatherMap :" + str(e))
            except ValueError as e:
                return format_error(e)
            else:
                self._current_ride = new_ride
                return {"success": True}
        else:
            return format_error("Aucun utilisateur n'est actuellement connecté")

    @check_params(object)
    def cancel_ride(self):
        """
        Annulation d'un trajet sauvegardé
        :return: {'success': Bool, ('error': 'message d'erreur' si success = False) }
        """
        if self._current_ride:
            self._current_ride = None
            return {"success": True}
        else:
            return format_error("Vous n'avez pas encore défini de trajet")

    @check_params(object, int, dict)
    def set_ride_precisions(self, travellers_number, luggage):
        """
        Définition ou modification des données détaillées du trajet préalablement sauvegardé
        :param travellers_number: nombre de voyageurs (int)
        :param luggage: bagages transportés (dict avec valeurs dans la liste des possibles)
        :return: {'success': Bool, ('error': 'message d'erreur' si success = False) }
        """
        if self._current_ride:
            try:
                self._current_ride.travellers = travellers_number
                self._current_ride.luggage = luggage
            except ValueError:
                return format_error("L'un des paramètres du trajet a une valeur inattendue")
            else:
                return {"success": True}
        else:
            return format_error("Vous n'avez pas encore défini de trajet")

    @check_params(object)
    def start_calculation(self):
        """
        Lancement du calcul d'itinéraires pour le trajet défini et sauvegardé
        :return: -  {'success': True,
                    'possible_routes': liste ordonnée d'itinéraires possibles de type Route (entre 0 et 3),
                    'unsuitable_routes': liste de modes de transports impossibles {'mode': mode, 'msg': message}
                OU BIEN
                -   {'success': False, 'error': 'message d'erreur' }
        """
        if self._current_ride:
            try:
                possible_routes, unsuitable_routes = self._current_ride.start_simulation()
            except TimeoutError as e:
                return format_error(e)
            except ApiCallError as e:
                return format_error(e)
            except ParamNotFoundError as e:
                return format_error(e)
            else:
                return {"success": True, "possible_routes": possible_routes, "unsuitable_routes": unsuitable_routes}
        else:
            return format_error("Vous n'avez pas encore défini de trajet")