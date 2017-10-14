# -*- coding: utf-8 -*-

# Critères de préférences pour un trajet
FASTEST  = "FASTEST"
SHORTEST = "SHORTEST"
CHEAPEST = "CHEAPEST"
EASIEST = "EASIEST"
NICEST = "NICEST"
LESS_WAKING = "LESS_WALKING"


class Ride():

    def __init__(self, start, end, departure_time):
        #self._user = user
        self.start = start
        self.end = end
        self.departure_time = departure_time