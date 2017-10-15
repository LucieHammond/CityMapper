# -*- coding: utf-8 -*-

from webservice.weather import Weather

# Critères de préférences pour un trajet
FASTEST  = "FASTEST"
SHORTEST = "SHORTEST"
CHEAPEST = "CHEAPEST"
EASIEST = "EASIEST"
NICEST = "NICEST"
LESS_WALKING = "LESS_WALKING"

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
        self._departure_time = departure_time  # timestamp

        self._travellers = 1
        self._luggage = dict()
        self._preferences = user.preferences
        self._weather = self._get_weather()

    @property
    def user(self):
        return self.user

    @property
    def weather(self):
        return self._weather

    @property
    def travellers(self):
        return self._travellers

    @travellers.setter
    def travellers(self, value):
        self._travellers = value

    @property
    def luggage(self):
        return self._luggage

    @luggage.setter
    def luggage(self, value):
        self._luggage = value

    @property
    def preferences(self):
        return self._preferences

    @preferences.setter
    def preferences(self, value):
        self._preferences = value

    def _get_weather(self):

        weather_service = Weather()
        weather = weather_service.get_from_api(self._departure_time)
        return weather
