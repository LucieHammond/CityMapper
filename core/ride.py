# -*- coding: utf-8 -*-

from webservice.weather import Weather
from routes.bicycling import VelibRoute
from routes.driving import AutolibRoute
from routes.transit import SubwayRoute
from core.tasks import TasksManager
from constants import FASTEST, SHORTEST, CHEAPEST, EASIEST, NICEST, LESS_WALKING, \
    SUITCASE, BULKY, BACKPACK, HANDBAG


class Ride(object):
    """ Trajet demandé par l'utilisateur, pour lequel on va calculer plusieurs itinéraires possibles """

    def __init__(self, user, start, end, departure_time):
        self._user = user
        self._start = start
        self._end = end
        self._departure_time = departure_time  # format = timestamp

        self._travellers = 1  # Nombre de voyageurs
        self._luggage = dict()

        # Par défault, les préférences pour le trajet sont celles définies dans le profil de l'utilisateur
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
        """ :type value: int """
        self._travellers = value

    @property
    def luggage(self):
        return self._luggage

    @luggage.setter
    def luggage(self, value):
        """ :type value: dict( {type_bagage : nombre, ...} ) """
        for bag in value.keys():
            if bag not in [SUITCASE, BULKY, BACKPACK, HANDBAG]:
                raise ValueError
        for val in value.values():
            if not isinstance(val, int) or val < 0:
                raise ValueError
        self._luggage = value

    @property
    def preferences(self):
        return self._preferences

    @preferences.setter
    def preferences(self, value):
        """ :type value: dict( {critère : note de 0 à 5, ...} ) """
        if sorted(value.keys()) != [CHEAPEST, EASIEST, FASTEST, LESS_WALKING, NICEST, SHORTEST]:
            raise ValueError
        for val in value.values():
            if val not in range(0, 6):
                raise ValueError
        self._preferences = value

    def _get_weather(self):
        """ Appelle l'API de Open Weather Map pour connaître la météo au moment du départ

        :return: {'temperature' (en Celsius), 'rain' (en mm sur 3h), 'snow' (en mm sur 3h), 'wind' (en m/s)}
        """
        weather_service = Weather()
        tm = TasksManager()
        tm.new_task(target=weather_service.get_from_api, args=(self._departure_time, ))
        weather = tm.next_result()
        return weather

    def start_simulation(self):
        """ Calcule les itinéraires possibles en Vélib, Autolib et Transports en commun

        - Si il y a au plus 1 itinéraire possible compte tenu des données du trajet, affiche le résultat
        - Sinon, lance une comparaison des itinéraires et affiche celui qui est renvoyé (le meilleur)

        """
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
            return None
        elif len(possible_routes) == 1:
            possible_routes[0].display_route()
            return possible_routes[0]
        else:
            scores = self._compute_scores(possible_routes)
            best_route = self._compare_routes(scores)
            best_route.display_route()
            return best_route

    def _is_velib_possible(self):
        """ Teste si l'utilisateur n'est pas trop jeune ou avec des bagages trop gros/nombreux pour prendre le Velib """
        nb_luggage = 0
        for item in self._luggage.keys():
            if item in [SUITCASE, BULKY]:
                return False
        return nb_luggage <= 4 and self._user.age >= 14

    def _is_autolib_possible(self):
        """ Teste si l'utilisateur est en droit de conduire une Autolib """
        return self._user.age >= 18 and self._user.driving_licence

    def _is_transit_possible(self):
        """ Teste si l'utilisateur n'a pas de bagages trop encombrants pour prendre les transports en commun """
        nb_luggage = 0
        for item in self._luggage.keys():
            if item == BULKY:
                return False
            nb_luggage += 1
        return nb_luggage <= 5 and self._user.age >= 7

    def _compute_scores(self, possible_routes):
        """ Calcule pour chaque itinéraire et pour chaque critère un score (float) entre 0 (meilleur) et 1 (moins bon)

        Les 6 critères sont :
        - le temps total
        - la distance totale
        - le prix
        - le nombre de changements
        - l'inconfort du trajet (météo mauvaise, charge à porter...)
        - le temps de marche à pied
        :param possible_routes: liste des itinéraires possibles (de type Route)
        :return: dictionnaire des scores {route1: {critère1: score1, critère2: note2 ...}, ... }

        """

        scores = dict.fromkeys(possible_routes, {})

        # Scores pour le temps
        min_time = min([route.time for route in possible_routes])
        max_time = max([route.time for route in possible_routes])
        for route in possible_routes:
            scores[route]["time"] = self._normalize_score(route.time, min_time, max_time)

        # Score pour la distance
        min_dist = min([route.distance for route in possible_routes])
        max_dist = max([route.distance for route in possible_routes])
        for route in possible_routes:
            scores[route]["distance"] = self._normalize_score(route.distance, min_dist, max_dist)

        # Score pour le prix
        min_price = min([route.price for route in possible_routes])
        max_price = max([route.price for route in possible_routes])
        for route in possible_routes:
            scores[route]["price"] = self._normalize_score(route.price, min_price, max_price)

        # Score pour le nombre de changements
        min_transfers = min([route.transfers_nb for route in possible_routes])
        max_transfers = max([route.transfers_nb for route in possible_routes])
        for route in possible_routes:
            scores[route]["transfers"] = self._normalize_score(route.transfers_nb, min_transfers, max_transfers)

        # Score pour l'inconfort
        min_discomfort = min([route.discomfort for route in possible_routes])
        max_discomfort = max([route.discomfort for route in possible_routes])
        for route in possible_routes:
            scores[route]["discomfort"] = self._normalize_score(route.discomfort, min_discomfort, max_discomfort)

        # Score pour le temps de marche à pied
        min_walking = min([route.walking_time for route in possible_routes])
        max_walking = max([route.walking_time for route in possible_routes])
        for route in possible_routes:
            scores[route]["walking"] = self._normalize_score(route.walking_time, min_walking, max_walking)

        return scores

    @staticmethod
    def _normalize_score(score, min_score, max_score):
        return (float(score) - float(min_score)) / (float(max_score) - float(min_score))

    def _compare_routes(self, scores, retry_nb=0):
        """ Compare les différents itinéraires en pondérant chacun de leurs scores par le coefficient de préférence
            associé au critère sur lequel porte le score

        NB: Si plusieurs itinéraires obtiennenent des notes pondérées identiques, on recommence en changeant légèrement
        les préférences (un critère modifié à la fois, dans l'ordre des choix par défault)

        :return: le meilleur itinéraire (de type Route) compte tenu des préférences de l'utilisateur

        """

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
