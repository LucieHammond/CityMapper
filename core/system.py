# -*- coding: utf-8 -*-

from user import User, IncoherentDateError
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


class HowToGoSystem(object):

    def __init__(self):
        self._users = list()
        self._current_user = None
        self._current_ride = None
        self._best_route = None

    @check_params(object, str, str, date)
    def sign_up(self, username, password, birthdate):
        try:
            new_user = User(username, password, birthdate)
        except IncoherentDateError as e:
            print(e)
        else:
            self._current_user = new_user
            self._users.append(new_user)

    @check_params(object, str, str)
    def sign_in(self, username, password):
        for user in self._users:
            if user.username == username and user.password == password:
                self._current_user = user
                return
        raise UserNotFoundError

    @check_params(object)
    def sign_out(self):
        if self._current_user:
            self._current_user = None
        else:
            print "Aucun utilisateur n'est actuellement connecté"

    @check_params(object, str, str, str, bool)
    def set_profile_settings(self, velib_subscription, autolib_subscription, subway_subscription, driving_licence):
        if self._current_user:
            self._current_user.set_subscriptions_infos(velib_subscription, autolib_subscription, subway_subscription)
            self._current_user.driving_licence = driving_licence
        else:
            print "Aucun utilisateur n'est actuellement connecté"

    @check_params(object, dict)
    def set_user_preferences(self, preferences):
        if self._current_user:
            self._current_user.preferences = preferences
        else:
            print "Aucun utilisateur n'est actuellement connecté"

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


class UserNotFoundError(Exception):
    def __str__(self):
        return "Le nom d'utilisateur ou le mot de passe est incorrect"


if __name__ == "__main__":
    sys = HowToGoSystem()
