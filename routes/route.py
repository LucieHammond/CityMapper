# -*- coding: utf-8 -*-

from constants import WALKING_MODE, BICYCLING_MODE
import math


class Route(object):

    def __init__(self, ride):
        self._ride = ride
        self._modes_breakdown = None
        self._steps = None

        self._time = None
        self._distance = None
        self._price = None
        self._transfers_nb = None
        self._walking_time = None
        self._weather_impact = None
        self._difficulty = None

    @property
    def steps(self):
        return self._steps

    @property
    def time(self):
        if self._time is None:
            self._time = 0
            for step in self._steps:
                self._time += step["time"]
        return self._time

    @property
    def distance(self):
        if self._distance is None:
            self._distance = 0
            for step in self._steps:
                self._distance += step["dist"]
        return self._distance

    @property
    def price(self):
        if self._price is None:
            self._price = self._compute_price()
        return self._price

    @property
    def transfers_nb(self):
        if self._transfers_nb is None:
            relevant_steps_nb = sum([1 for step in self._steps if step["mode"] != WALKING_MODE])
            self._transfers_nb = max(0, relevant_steps_nb - 1)
        return self._transfers_nb

    @property
    def weather_impact(self):
        if self._weather_impact is None:
            self._weather_impact = self._compute_weather_impact()
        return self._weather_impact

    @property
    def difficulty(self):
        if self._difficulty is None:
            self._difficulty = self._compute_difficulty()
        return self._difficulty

    @property
    def walking_time(self):
        if self._walking_time is None:
            self._walking_time = self._modes_breakdown[WALKING_MODE]
        return self._walking_time

    def calculate_route(self):
        raise NotImplementedError

    def _compute_price(self):
        raise NotImplementedError

    def _compute_weather_impact(self):
        weather = self._ride.weather

        # Définition d'un barême approximatif qui traduit l'impact météorologique ressenti
        # Key = (valeur min exclue, valeur max inclue)
        rain_scores = {(-1, 0): -20, (0, 1): 30, (1, 5): 50, (5, 20): 80, (20, 50): 120, (50, 500): 200}
        snow_scores = {(-1, 0): -5, (0, 2): 40, (2, 4): 60, (4, 8): 80, (8, 30): 100, (30, 300): 200}
        wind_scores = {(-1, 0.5): 0, (0.5, 3): 5, (3, 8): 15, (8, 14): 30, (14, 20): 50, (20, 24): 75, (24, 28): 105,
                       (28, 33): 140, (33, 200): 200}
        temp_scores = {(-273, -10): 200, (-10, 0): 120, (0, 10): 50, (10, 20): 10, (20, 30): -10, (30, 40): 10,
                       (40, 50): 60, (50, 60): 160, (60, 150): 200}

        impact = 0
        for interval in rain_scores.keys():
            if interval[0] < weather["rain"] <= interval[1]:
                impact += rain_scores[interval]
                break
        for interval in snow_scores.keys():
            if interval[0] < weather["snow"] <= interval[1]:
                impact += snow_scores[interval]
                break
        for interval in wind_scores.keys():
            if interval[0] < weather["wind"] <= interval[1]:
                impact += wind_scores[interval]
                break
        for interval in temp_scores.keys():
            if interval[0] < weather["temperature"] <= interval[1]:
                impact += temp_scores[interval]
                break

        # L'impact global sera proportionnel à la racine du temps passé à Vélo et du temps passé à pied
        # (le temps à vélo compte davantage que le temps à pied, les coefficients sont différents)
        bicycling_time = self._modes_breakdown[BICYCLING_MODE] if BICYCLING_MODE in self._modes_breakdown.keys() else 0
        factor = math.sqrt(self.walking_time/3000.0 + bicycling_time/1500.0)
        return impact * factor

    def _compute_difficulty(self):
        raise NotImplementedError
