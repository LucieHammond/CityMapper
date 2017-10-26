# -*- coding: utf-8 -*-

from user import User
from ride import Ride
from datetime import date
import re
from webservice.api_manager import ApiCallError, ParamNotFoundError
from webservice.geocode import Geocode, ZeroResultsError
from tasks import TasksManager, TimeoutError

#todo récupérer les exceptions


# Vérifie le type des arguments des fonctions appelables du système
def check_params(*types):
    def params_accepts(funct):
        def new_function(*args, **kwargs):
            for (a, t) in zip(args, types):
                assert isinstance(a, t)
            return funct(*args, **kwargs)

        return new_function
    return params_accepts


def format_error(message):
    print message
    return {"success": False, "error": message}


class HowToGoSystem(object):

    def __init__(self):
        self._users = list()
        self._current_user = None
        self._current_ride = None
        self._best_route = None

    @property
    def current_user(self):
        return self._current_user

    @property
    def current_ride(self):
        return self._current_ride

    @check_params(object, basestring, basestring, date)
    def sign_up(self, username, password, birthdate):
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
        for user in self._users:
            if user.username == username and user.password == password:
                self._current_user = user
                return {"success": True}
        return format_error("Le nom d'utilisateur ou le mot de passe est incorrect")

    @check_params(object)
    def sign_out(self):
        if self._current_user:
            self._current_user = None
            return {"success": True}
        else:
            return format_error("Aucun utilisateur n'est actuellement connecté")

    @check_params(object, basestring, basestring, basestring, bool, dict)
    def set_profile_settings(self, velib, autolib, subway, driving_licence, preferences):
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
        if self._current_user:
            start, end = None, None

            # Si l'adresse est déjà renseignée en temps que coordonnées sous la forme "$ longitude,latitude"
            re_start = re.match('^\$ (\d+.\d+), ?(\d+.\d+)$', start_address)
            if re_start:
                start = (float(re_start.group(1)), float(re_start.group(2)))
            re_end = re.match('^\$ (\d+.\d+), ?(\d+.\d+)$', end_address)
            if re_end:
                start = (float(re_end.group(1)), float(re_end.group(2)))

            # Convertir l'adresse en coordonnées géographiques
            try:
                geocode = Geocode()
                tm = TasksManager()
                if not start: tm.new_task(target=geocode.get_from_api, args=(start_address,))
                if not end: tm.new_task(target=geocode.get_from_api, args=(end_address,))
                if not start: start = tm.next_result()
                if not end: end = tm.next_result()
            except TimeoutError as e:
                return format_error(e.message)
            except ApiCallError as e:
                return format_error("Géocode: " + e.message)
            except ZeroResultsError as e:
                return format_error(e.message)
            except ParamNotFoundError as e:
                return format_error("Géocode: " + e.message)

            try:
                new_ride = Ride(self._current_user, start, end, departure_time)
            except TimeoutError as e:
                return format_error(e.message)
            except ApiCallError as e:
                return format_error("WeatherMap :" + e.message)
            except ParamNotFoundError as e:
                return format_error("WeatherMap :" + e.message)
            else:
                self._current_ride = new_ride
                return {"success": True}
        else:
            return format_error("Aucun utilisateur n'est actuellement connecté")

    @check_params(object)
    def reset_ride(self):
        if self._current_ride:
            self._current_ride = None
            return {"success": True}
        else:
            return format_error("Vous n'avez pas encore défini de trajet")

    @check_params(object, int, dict)
    def set_ride_precisions(self, travellers_number, luggage):
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

    @check_params(object, dict)
    def set_ride_preferences(self, preferences):
        if self._current_ride:
            self._current_ride.preferences = preferences
        else:
            print "Vous n'avez pas encore défini de trajet"

    @check_params(object)
    def start_calculation(self):
        possible_routes, unsuitable_routes = self._current_ride.start_simulation()
