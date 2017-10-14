# -*- coding: utf-8 -*-

from ride import FASTEST, SHORTEST, CHEAPEST, EASIEST, NICEST, LESS_WAKING
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
        self._preferences = {FASTEST: 4, SHORTEST: 0, CHEAPEST: 3, EASIEST: 2, NICEST: 5, LESS_WAKING: 1}

    @property
    def username(self):
        return self._username

    def set_subscriptions_infos(self, velib, autolib, subway):
        self._subscriptions = {"velib": velib, "autolib": autolib, "subway": subway}

    def set_preferences(self, fastest, shortest, cheapest, easiest, nicest, less_walking):
        self._preferences = {FASTEST: fastest,
                             SHORTEST: shortest,
                             CHEAPEST: cheapest,
                             EASIEST: easiest,
                             NICEST: nicest,
                             LESS_WAKING: less_walking}
