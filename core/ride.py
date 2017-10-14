# -*- coding: utf-8 -*-

# Critères de préférences pour un trajet
FASTEST  = "FASTEST"
SHORTEST = "SHORTEST"
CHEAPEST = "CHEAPEST"
EASIEST = "EASIEST"
NICEST = "NICEST"
LESS_WAKING = "LESS_WALKING"

# Types de bagages
SUITCASE = "SUITCASE"
BACKPACK = "BACKPACK"
HANDBAG = "HANDBAG"
BULKY = "BULKY"


class Ride():

    def __init__(self, user, start, end, departure_time):
        self._user = user
        self._start = start
        self._end = end
        self._departure_time = departure_time

        self._travellers = 1
        self._luggage = dict()
        self._preferences = user.preferences

    @property
    def travellers(self):
        return self.travellers

    @travellers.setter
    def travellers(self, value):
        self._travellers = value

    @property
    def luggage(self):
        return self.luggage

    @luggage.setter
    def luggage(self, value):
        self._luggage = value

    @property
    def preferences(self):
        return self.preferences

    @preferences.setter
    def preferences(self, value):
        self._preferences = value


