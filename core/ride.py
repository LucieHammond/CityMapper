# -*- coding: utf-8 -*-

from webservice.weather import Weather
from routes.bicycling import VelibRoute
from routes.driving import AutolibRoute
from routes.transit import SubwayRoute

# Critères de préférences pour un trajet
FASTEST = "FASTEST"
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


class Ride:

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
        return self._user

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def departure_time(self):
        return self._departure_time

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

    def start_simulation(self):
        possible_routes = list()

        if self._is_velib_possible():
            velib_route = VelibRoute(self)
            velib_route.calculate_route()
            possible_routes.append(velib_route)
        if self._is_autolib_possible():
            autolib_route = AutolibRoute(self)
            autolib_route.calculate_route()
            possible_routes.append(autolib_route)
        if self._is_transit_possible():
            subway_route = SubwayRoute(self)
            subway_route.calculate_route()
            possible_routes.append(subway_route)

        if len(possible_routes) == 0:
            print "Désolé, aucun des moyens de transports proposé n'est adapté pour vous."
        elif len(possible_routes) == 1:
            return possible_routes[0]
        else:
            scores = self._compute_scores(possible_routes)
            best_route = self._compare_routes(scores)
            best_route.display_route()

    def _is_velib_possible(self):
        for item in self._luggage.keys():
            if item in [SUITCASE, BULKY]:
                return False
        return self._user.age >= 14

    def _is_autolib_possible(self):
        return self._user.age >= 18 and self._user.driving_licence

    def _is_transit_possible(self):
        for item in self._luggage.keys():
            if item == BULKY:
                return False
        return self._user.age >= 7

    def _compute_scores(self, possible_routes):

        scores = dict.fromkeys(possible_routes, {})

        # Optimize time (take fastest)
        min_time = min([route.time for route in possible_routes])
        max_time = max([route.time for route in possible_routes])
        for route in possible_routes:
            scores[route]["time"] = self._normalize_score(route.time, min_time, max_time)

        # Optimize distance (take shortest)
        min_dist = min([route.distance for route in possible_routes])
        max_dist = max([route.distance for route in possible_routes])
        for route in possible_routes:
            scores[route]["distance"] = self._normalize_score(route.distance, min_dist, max_dist)

        # Optimize price (take cheapest)
        min_price = min([route.price for route in possible_routes])
        max_price = max([route.price for route in possible_routes])
        for route in possible_routes:
            scores[route]["price"] = self._normalize_score(route.price, min_price, max_price)

        # Optimize number of transfers (take easiest)
        min_transfers = min([route.transfers_nb for route in possible_routes])
        max_transfers = max([route.transfers_nb for route in possible_routes])
        for route in possible_routes:
            scores[route]["transfers"] = self._normalize_score(route.transfers_nb, min_transfers, max_transfers)

        # Optimize discomfort (take nicest)
        min_discomfort = min([route.discomfort for route in possible_routes])
        max_discomfort = max([route.discomfort for route in possible_routes])
        for route in possible_routes:
            scores[route]["discomfort"] = self._normalize_score(route.discomfort, min_discomfort, max_discomfort)

        # Optimize walking time (take less walking)
        min_walking = min([route.walking_time for route in possible_routes])
        max_walking = max([route.walking_time for route in possible_routes])
        for route in possible_routes:
            scores[route]["walking"] = self._normalize_score(route.walking_time, min_walking, max_walking)

        return scores

    @staticmethod
    def _normalize_score(score, min_score, max_score):
        return (float(score) - float(min_score)) / (float(max_score) - float(min_score))

    def _compare_routes(self, scores, retry_nb=0):

        # Compute global grade
        best_grade = -1
        best_routes = list()
        preferences = self._user.preferences
        if retry_nb > 0:
            pref_to_change = [NICEST, FASTEST, CHEAPEST, EASIEST, LESS_WALKING, SHORTEST][retry_nb - 1]
            preferences[pref_to_change] += 1
        for route, score in scores.items():
            grade = 0
            grade += preferences[FASTEST] * score["time"]
            grade += preferences[SHORTEST] * score["distance"]
            grade += preferences[CHEAPEST] * score["price"]
            grade += preferences[EASIEST] * score["transfers"]
            grade += preferences[NICEST] * score["discomfort"]
            grade += preferences[LESS_WALKING] * score["walking"]
            scores[route]["grade"] = grade

            if best_grade == -1 or grade < best_grade:
                best_grade = grade
                best_routes = list([route])
            elif grade == best_grade:
                best_routes.append(route)

        if len(best_routes) == 1 or retry_nb == 6:
            return best_routes[0]
        else:
            new_scores = {route: scores[route] for route in best_routes}
            return self._compare_routes(new_scores, retry_nb + 1)
