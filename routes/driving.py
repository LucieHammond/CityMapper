# -*- coding: utf-8 -*-

from route import Route
from webservice.autolib import Autolib
from webservice.directions import Directions
from core.tasks import TasksManager
from constants import WALKING_MODE, DRIVING_MODE, FASTEST, SHORTEST, LESS_WALKING, CHEAPEST, \
    AUTOLIB_FIRST_RENTING_OFFER, AUTOLIB_PRET_A_ROULER, AUTOLIB_PREMIUM
import time

ONE_HOUR = 3600


class AutolibRoute(Route):
    """ Itinéraire en Autolib correspondant au trajet demandé """

    def __init__(self, ride):
        Route.__init__(self, ride)
        self._start_station = None
        self._end_station = None

    @property
    def start_station(self):
        return self._start_station

    @property
    def end_station(self):
        return self._end_station

    def calculate_route(self):
        """ Calcule l'itinéraire exact le plus adapté aux préférences de l'utilisateur

        Le calcul se fait grâce aux données récupérées depuis les APIs Open Data Autolib et Google Map
        Met à jour les paramêtres de l'objet (initialisés à None pour la plupart) avec l'itinéraire calculé
        """

        autolib = Autolib()
        directions = Directions()
        ride = self._ride

        # Critères de préférence pour la différentiation des itinéraires similaires
        search_criterion = self._define_search_criteria()

        # On va vérifier les places displonibles uniquement si le départ a lieu dans moins d'une heure
        real_time = (ride.departure_time - time.time() < ONE_HOUR)

        # Cherche les 3 stations disponibles les plus proches du départ
        def seek_starting_routes():
            stations = autolib.get_from_api(ride.start, True, real_time)
            tm_start = TasksManager()
            for station in stations:
                tm_start.new_task(target=directions.get_from_api, args=(ride.start, station["geo_point"], WALKING_MODE))
            return {"stations": stations, "routes": tm_start}

        # Cherche les 3 stations disponibles les plus proches de l'arrivée
        def seek_ending_routes():
            stations = autolib.get_from_api(ride.end, False, real_time)
            tm_end = TasksManager()
            for station in stations:
                tm_end.new_task(target=directions.get_from_api, args=(station["geo_point"], ride.end, WALKING_MODE))
            return {"stations": stations, "routes": tm_end}

        # Appelle simultanément les fonctions pour chercher les stations de départ et d'arrivée
        walking_routes = TasksManager()
        walking_routes.new_task(target=seek_starting_routes)
        walking_routes.new_task(target=seek_ending_routes)

        start_data = walking_routes.next_result()
        start_stations, start_routes = start_data["stations"], start_data["routes"].results_list()
        end_data = walking_routes.next_result()
        end_stations, end_routes = end_data["stations"], end_data["routes"].results_list()

        if len(start_stations) == 0 or len(end_stations) == 0:
            return False

        # Calcule les itinéraires en voiture pour toutes les combinaisons possibles (9 appels au maximum)
        driving_routes = TasksManager()
        for start_station in start_stations:
            for end_station in end_stations:
                driving_routes.new_task(target=directions.get_from_api,
                                        args=(start_station["geo_point"], end_station["geo_point"], DRIVING_MODE))

        # Compare les itinéraires possibles et renvoie le meilleur compte tenu des préférences de l'utilisateur
        if search_criterion == FASTEST:
            best_start, best_end, best_autolib = self._optimize_time(start_stations, end_stations, start_routes,
                                                                     end_routes, driving_routes)
        elif search_criterion == SHORTEST:
            best_start, best_end, best_autolib = self._optimize_dist(start_stations, end_stations, start_routes,
                                                                     end_routes, driving_routes)
        else:
            best_start, best_end, best_autolib = self._optimize_walking(start_stations, end_stations, start_routes,
                                                                        end_routes, driving_routes.results_list())

        # On peut maintenant définir les caractéristiques de la route trouvée
        self._start_station = start_stations[best_start]
        self._end_station = end_stations[best_end]

        start_routes[best_start].update({"mode": WALKING_MODE})
        end_routes[best_end].update({"mode": WALKING_MODE})
        best_autolib.update({"mode": DRIVING_MODE})
        self._steps = list([start_routes[best_start], best_autolib, end_routes[best_end]])
        self._modes_breakdown = {WALKING_MODE: self._steps[0]["time"] + self._steps[2]["time"],
                                 DRIVING_MODE: self._steps[1]["time"]}
        return True

    def _define_search_criteria(self):
        """ Analyse les préférences de l'utilisateur pour déterminer le critère de sélection le plus adapté
        Le critère est cherché parmi ceux qui sont pertinents pour différencier deux trajets similaires en Autolib

        :return: critère de recherche préféré parmi FASTEST, LESS_WALKING, SHORTEST

        """
        preferences = self._ride.preferences

        # Le prix du trajet dépend uniquement du temps pour un forfait donné donc CHEAPEST sera assimilé à FASTEST
        relevant_criteria = [FASTEST, LESS_WALKING, SHORTEST, CHEAPEST]
        best_criterion = FASTEST
        grade = 5
        while grade >= 0:
            criteria = [c for c, v in preferences.items() if v == grade and c in relevant_criteria]
            if len(criteria) > 1:
                best_criterion = FASTEST if FASTEST in criteria or CHEAPEST in criteria else LESS_WALKING
                break
            elif len(criteria) == 1:
                best_criterion = criteria[0] if criteria[0] != CHEAPEST else FASTEST
                break
            else:
                grade -= 1

        return best_criterion

    @staticmethod
    def _optimize_time(start_stations, end_stations, start_routes, end_routes, driving_routes):
        """ Garde l'itinéraire celui qui minimise le temps de parcours """
        time_min = -1
        best_start = 0
        best_end = 0
        best_velib_route = None
        for start, start_station in enumerate(start_stations):
            time_start = start_routes[start]["time"]
            for end, end_station in enumerate(end_stations):
                time_end = end_routes[end]["time"]
                route = driving_routes.next_result()
                total_time = route["time"] + time_start + time_end
                if time_min == -1 or total_time < time_min:
                    time_min = total_time
                    best_start = start
                    best_end = end
                    best_velib_route = route
        return best_start, best_end, best_velib_route

    @staticmethod
    def _optimize_dist(start_stations, end_stations, start_routes, end_routes, driving_routes):
        """ Garde l'itinéraire qui minimise la distance parcourue """
        dist_min = -1
        best_start = 0
        best_end = 0
        best_velib_route = None
        for start, start_station in enumerate(start_stations):
            dist_start = start_routes[start]["dist"]
            for end, end_station in enumerate(end_stations):
                dist_end = end_routes[end]["dist"]
                route = driving_routes.next_result()
                total_dist = route["dist"] + dist_start + dist_end
                if dist_min == -1 or total_dist < dist_min:
                    dist_min = total_dist
                    best_start = start
                    best_end = end
                    best_velib_route = route
        return best_start, best_end, best_velib_route

    @staticmethod
    def _optimize_walking(start_stations, end_stations, start_routes, end_routes, driving_routes):
        """ Garde l'itinéraire qui minimise le temps de marche """
        time_min = -1
        best_start = 0
        best_end = 0
        for start, start_station in enumerate(start_stations):
            time_start = start_routes[start]["time"]
            if time_min == -1 or time_start < time_min:
                time_min = time_start
                best_start = start
        time_min = -1
        for end, end_station in enumerate(end_stations):
            time_end = end_routes[end]["time"]
            if time_min == -1 or time_end < time_min:
                time_min = time_end
                best_end = end
        return best_start, best_end, driving_routes[best_end * len(start_stations) + best_start]

    def _compute_price(self):
        """ Calcule le prix exact de l'itinéraire finalement choisi """

        subscription = self._ride.user.subscriptions["autolib"]
        time_autolib = self._modes_breakdown[DRIVING_MODE]
        if subscription == AUTOLIB_FIRST_RENTING_OFFER:
            time_autolib = max([0, time_autolib - 30 * 60])

        if subscription in [AUTOLIB_PRET_A_ROULER, AUTOLIB_FIRST_RENTING_OFFER]:
            return round(time_autolib / 60.0 * 0.3166, 2)
        elif subscription == AUTOLIB_PREMIUM:
            return round(time_autolib / 60.0 * 0.2333, 2)

    def _compute_difficulty(self):
        """ Le degré d'inconfort lié aux bagages est nul pour un trajet en voiture """

        return 0
