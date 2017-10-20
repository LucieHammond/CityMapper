# -*- coding: utf-8 -*-

from routes.route import Route
from webservice.velib import Velib
from webservice.directions import Directions, WALKING_MODE, BICYCLING_MODE
import time

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

    def _calculate_route(self):

        # todo think about the impact of bonuses
        # todo utiliser le multithreading

        velib = Velib()
        directions = Directions()
        ride = self._ride

        real_time = True
        if ride.departure_time - time.time() > ONE_HOUR:
            real_time = False

        # Cherche les 3 stations disponibles les plus proches du départ
        start_stations = velib.get_from_api(ride.start, True, real_time)
        start_routes = list()
        for station in start_stations:
            route_to_station = directions.get_from_api(ride.start, station["position"], WALKING_MODE)
            start_routes.append(route_to_station)

        # Cherche les 3 stations disponibles les plus proches de l'arrivée
        end_stations = velib.get_from_api(ride.end, False, real_time)
        end_routes = list()
        for station in end_stations:
            route_from_station = directions.get_from_api(station["position"], ride.end, WALKING_MODE)
            end_routes.append(route_from_station)

        # Calcule les itinéraires à vélo pour toutes les combinaisons possibles (9 appels au maximum)
        # Garde celui qui minimise le temps de parcours (= seul paramêtre qui fait le différance ici avec le bonus)
        time_min = -1
        best_start = 0
        best_end = 0
        best_velib_route = None
        for start, start_station in enumerate(start_stations):
            time_start = start_routes[start]["time"]
            for end, end_station in enumerate(end_stations):
                time_end = end_routes[end]["time"]
                route = directions.get_from_api(start_station["position"], end_station["position"], BICYCLING_MODE)
                total_time = route["time"] + time_start + time_end
                if time_min == -1 or total_time < time_min:
                    time_min = total_time
                    best_start = start
                    best_end = end
                    best_velib_route = route

        # On peut maintenant définir les caractéristiques de la route trouvée
        self._start_station = start_stations[best_start]
        self._end_station = end_stations[best_end]

        start_routes[best_start].update({"mode": WALKING_MODE})
        end_routes[best_end].update({"mode": WALKING_MODE})
        best_velib_route.update({"mode": BICYCLING_MODE})
        self._steps = list([start_routes[best_start], best_velib_route, end_routes[best_end]])

        self._time = time_min
        self._distance = self._steps[0]["dist"] + self._steps[1]["dist"] + self._steps[2]["dist"]
        self._modes_breakdown = {WALKING_MODE: self._steps[0]["time"] + self._steps[2]["time"],
                                 BICYCLING_MODE: self._steps[1]["time"]}

'''from core.ride import Ride

start = (48.836239, 2.242632)
end = (48.839659, 2.290922)

ride = Ride(start, end, time.time() + 25000)

velib_route = VelibRoute(ride)
print(velib_route._start_station)
print(velib_route._end_station)
print(velib_route._steps)
print(velib_route._time)
print(velib_route._distance)
print(velib_route._modes_breakdown)'''




