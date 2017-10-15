# -*- coding: utf-8 -*-

from ride import FASTEST, SHORTEST, CHEAPEST, EASIEST, NICEST, LESS_WALKING
from routes import bicycling, driving, transit


class User:

    total_users = 0

    def __init__(self, username, password, age):
        User.total_users += 1
        self._id = User.total_users
        self._username = username
        self._password = password
        self._age = age
        self._subscriptions = {"velib": bicycling.NO_SUBSCRIPTION,
                               "autolib": driving.PRET_A_ROULER,
                               "subway": transit.NO_RATP_TITLE}
        self._driving_licence = True
        self._preferences = {FASTEST: 4, SHORTEST: 0, CHEAPEST: 3, EASIEST: 2, NICEST: 5, LESS_WALKING: 1}

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def preferences(self):
        return self._preferences

    @preferences.setter
    def preferences(self, value):
        self._preferences = value

    @property
    def driving_licence(self):
        return self._driving_licence

    @driving_licence.setter
    def driving_licence(self, value):
        self._driving_licence = value

    @property
    def subscriptions(self):
        return self._subscriptions

    def set_subscriptions_infos(self, velib, autolib, subway):
        self._subscriptions = {"velib": velib, "autolib": autolib, "subway": subway}

    def print_user_infos(self, detailed=False):
        print "Utilisateur {} : {} ({} ans)".format(self._id, self._username, self._age)
        if detailed:
            print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - "
            print "Abonnements :"
            print " - Velib :", self._subscriptions["velib"]
            print " - Autolib :", self._subscriptions["autolib"]
            print " - Transports en commun :", self._subscriptions["subway"]
            print "Préférences :"
            for preference, value in self._preferences.items():
                print " - {} : {}".format(preference, str(value))
            print "Permis de conduire : {}\n".format("Oui" if self._driving_licence else "Non")
