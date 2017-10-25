# -*- coding: utf-8 -*-

from user import User
from ride import Ride
from datetime import date

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

    @check_params(object, str, str, date)
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

    @check_params(object, str, str)
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
        else:
            print "Aucun utilisateur n'est actuellement connecté"

    @check_params(object, str, str, str, bool, dict)
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

    @check_params(object, tuple, tuple, float)
    def new_ride(self, start, end, departure_time):
        # todo gérer les adresse en chaines de caractères
        if self._current_user:
            new_ride = Ride(self._current_user, start, end, departure_time)
            self._current_ride = new_ride
        else:
            print "Aucun utilisateur n'est actuellement connecté"

    @check_params(object)
    def cancel_ride(self):
        if self._current_ride:
            self._current_ride = None
        else:
            print "Vous n'avez pas encore défini de trajet"

    @check_params(object, int, dict)
    def set_ride_precisions(self, travellers_number, luggage):
        if self._current_ride:
            self._current_ride.travellers = travellers_number
            self._current_ride.luggage = luggage
        else:
            print "Vous n'avez pas encore défini de trajet"

    @check_params(object, dict)
    def set_ride_preferences(self, preferences):
        if self._current_ride:
            self._current_ride.preferences = preferences
        else:
            print "Vous n'avez pas encore défini de trajet"

    @check_params(object)
    def start_calculation(self):
        possible_routes, unsuitable_routes = self._current_ride.start_simulation()

    def display_users(self):
        for user in self._users:
            user.print_user_infos()

    def display_user_profile(self):
        if self._current_user:
            self._current_user.print_user_infos(True)
        else:
            print "Aucun utilisateur n'est actuellement connecté"
