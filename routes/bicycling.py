# -*- coding: utf-8 -*-

from route import Route
from webservice.velib import Velib
from webservice.directions import Directions, WALKING_MODE, BICYCLING_MODE
import time
from core.tasks import TasksManager


ONE_HOUR = 3600

# Forfaits Velib possibles
SUBSCRIPTION_30M = "VELIB_SUBSCRIPTION_30M"
SUBSCRIPTION_45M = "VELIB_SUBSCRIPTION_45M"
TICKETS_30M = "VELIB_TICKETS_30M"
NO_SUBSCRIPTION = "VELIB_NO_SUBSCRIPTION"


class VelibRoute(Route):

    def __init__(self, ride):
        self._start_station = None
        self._end_station = None
        self._steps = None
        Route.__init__(self, ride)

    @staticmethod
    def _optimize_route(start_stations, end_stations, start_routes, end_routes, bicycling_routes):
        # Garde celui qui minimise le temps de parcours (= seul paramêtre qui fait le différance ici avec le bonus)
        time_min = -1
        best_start = 0
        best_end = 0
        best_velib_route = None
        for start, start_station in enumerate(start_stations):
            time_start = start_routes[start]["time"]
            for end, end_station in enumerate(end_stations):
                time_end = end_routes[end]["time"]
                route = bicycling_routes.next_result()
                total_time = route["time"] + time_start + time_end
                if time_min == -1 or total_time < time_min:
                    time_min = total_time
                    best_start = start
                    best_end = end
                    best_velib_route = route
        return best_start, best_end, best_velib_route

    def calculate_route(self):

        # todo think about the impact of bonuses and less or more walking

        velib = Velib()
        directions = Directions()
        ride = self._ride

        real_time = True
        if ride.departure_time - time.time() > ONE_HOUR:
            real_time = False

        # Cherche les 3 stations disponibles les plus proches du départ
        def seek_starting_routes():
            start_stations = velib.get_from_api(ride.start, True, real_time)
            tm_start = TasksManager()
            for station in start_stations:
                tm_start.new_task(target=directions.get_from_api, args=(ride.start, station["position"], WALKING_MODE))
            return {"stations":start_stations, "routes": tm_start}

        # Cherche les 3 stations disponibles les plus proches de l'arrivée
        def seek_ending_routes():
            end_stations = velib.get_from_api(ride.end, False, real_time)
            tm_end = TasksManager()
            for station in end_stations:
                tm_end.new_task(target=directions.get_from_api, args=(station["position"], ride.end, WALKING_MODE))
            return {"stations": end_stations, "routes": tm_end}

        walking_routes = TasksManager()
        walking_routes.new_task(target=seek_starting_routes)
        walking_routes.new_task(target=seek_ending_routes)

        start_data = walking_routes.next_result()
        start_stations = start_data["stations"]
        start_routes = start_data["routes"].results_list()
        end_data = walking_routes.next_result()
        end_stations = end_data["stations"]
        end_routes = end_data["routes"].results_list()

        # Calcule les itinéraires à vélo pour toutes les combinaisons possibles (9 appels au maximum)
        bicycling_routes = TasksManager()
        for start_station in start_stations:
            for end_station in end_stations:
                bicycling_routes.new_task(target=directions.get_from_api,
                                          args=(start_station["position"], end_station["position"], BICYCLING_MODE))

        # Compare les itinéraires possibles et renvoie le mailleur suivant les critère de l'utilisateur
        best_start, best_end, best_velib_route = self._optimize_route(start_stations, end_stations, start_routes,
                                                                      end_routes, bicycling_routes)

        # On peut maintenant définir les caractéristiques de la route trouvée
        self._start_station = start_stations[best_start]
        self._end_station = end_stations[best_end]

        start_routes[best_start].update({"mode": WALKING_MODE})
        end_routes[best_end].update({"mode": WALKING_MODE})
        best_velib_route.update({"mode": BICYCLING_MODE})
        self._steps = list([start_routes[best_start], best_velib_route, end_routes[best_end]])

        self._time = self._steps[0]["time"] + self._steps[1]["time"] + self._steps[2]["time"]
        self._distance = self._steps[0]["dist"] + self._steps[1]["dist"] + self._steps[2]["dist"]
        self._modes_breakdown = {WALKING_MODE: self._steps[0]["time"] + self._steps[2]["time"],
                                 BICYCLING_MODE: self._steps[1]["time"]}
