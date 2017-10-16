# -*- coding: utf-8 -*-

from route import Route, WALKING_MODE, BICYCLING_MODE
from core.ride import FASTEST, SHORTEST, LESS_WALKING, CHEAPEST, BACKPACK, HANDBAG
from webservice.velib import Velib
from webservice.directions import Directions
import time
from core.tasks import TasksManager


ONE_HOUR = 3600

# Forfaits Velib possibles
SUBSCRIPTION_30M = "VELIB_SUBSCRIPTION_30M"
SUBSCRIPTION_45M = "VELIB_SUBSCRIPTION_45M"
TICKETS_30M = "VELIB_TICKETS_30M"
NO_SUBSCRIPTION = "VELIB_NO_SUBSCRIPTION"
ONE_TICKET_PRICE = 1.70


class VelibRoute(Route):

    def __init__(self, ride):
        Route.__init__(self, ride)
        self._start_station = None
        self._end_station = None

    def calculate_route(self):

        velib = Velib()
        directions = Directions()
        ride = self._ride
        search_criterion, check_price = self._define_search_criteria()
        real_time = (ride.departure_time - time.time() < ONE_HOUR)

        # Cherche les 3 stations disponibles les plus proches du départ
        def seek_starting_routes():
            stations = velib.get_from_api(ride.start, True, real_time)
            tm_start = TasksManager()
            for station in stations:
                tm_start.new_task(target=directions.get_from_api, args=(ride.start, station["position"], WALKING_MODE))
            return {"stations": stations, "routes": tm_start}

        # Cherche les 3 stations disponibles les plus proches de l'arrivée
        def seek_ending_routes():
            stations = velib.get_from_api(ride.end, False, real_time)
            tm_end = TasksManager()
            for station in stations:
                tm_end.new_task(target=directions.get_from_api, args=(station["position"], ride.end, WALKING_MODE))
            return {"stations": stations, "routes": tm_end}

        # Appelle simultanément les fonctions pour chercher les stations de départ et d'arrivée
        walking_routes = TasksManager()
        walking_routes.new_task(target=seek_starting_routes)
        walking_routes.new_task(target=seek_ending_routes)

        start_data = walking_routes.next_result()
        start_stations, start_routes = start_data["stations"], start_data["routes"].results_list()
        end_data = walking_routes.next_result()
        end_stations, end_routes = end_data["stations"], end_data["routes"].results_list()

        # Calcule les itinéraires à vélo pour toutes les combinaisons possibles (9 appels au maximum)
        bicycling_routes = TasksManager()
        for start_station in start_stations:
            for end_station in end_stations:
                bicycling_routes.new_task(target=directions.get_from_api,
                                          args=(start_station["position"], end_station["position"], BICYCLING_MODE))

        # Compare les itinéraires possibles et renvoie le meilleur suivant les critère de l'utilisateur
        if check_price:
            b_start, b_end, b_velib = self._check_price(search_criterion, start_stations, end_stations, start_routes,
                                                        end_routes, bicycling_routes)
        else:
            b_start, b_end, b_velib = self._optimize_route(search_criterion, start_stations, end_stations, start_routes,
                                                           end_routes, bicycling_routes)

        # On peut maintenant définir les caractéristiques de la route trouvée
        self._start_station = start_stations[b_start]
        self._end_station = end_stations[b_end]

        start_routes[b_start].update({"mode": WALKING_MODE})
        end_routes[b_end].update({"mode": WALKING_MODE})
        b_velib.update({"mode": BICYCLING_MODE})
        self._steps = list([start_routes[b_start], b_velib, end_routes[b_end]])
        self._modes_breakdown = {WALKING_MODE: self._steps[0]["time"] + self._steps[2]["time"],
                                 BICYCLING_MODE: self._steps[1]["time"]}

    def _define_search_criteria(self):
        preferences = self._ride.preferences
        relevant_criteria = [FASTEST, LESS_WALKING, SHORTEST]
        best_criterion = FASTEST
        grade = 5
        while grade >= 0:
            criteria = [c for c, v in preferences.items() if v == grade and c in relevant_criteria]
            if len(criteria) > 1:
                best_criterion = FASTEST if FASTEST in criteria else LESS_WALKING
                break
            elif len(criteria) == 1:
                best_criterion = criteria[0]
                break
            else:
                grade -= 1

        check_price = (preferences[CHEAPEST] >= grade)
        return best_criterion, check_price

    def _optimize_route(self, criterion, start_sts, end_sts, start_rts, end_rts, bicycling_rts):
        if criterion == FASTEST:
            return self._optimize_time(start_sts, end_sts, start_rts, end_rts, bicycling_rts)
        elif criterion == SHORTEST:
            return self._optimize_dist(start_sts, end_sts, start_rts, end_rts, bicycling_rts)
        else:
            return self._optimize_walking(start_sts, end_sts, start_rts, end_rts, bicycling_rts.results_list())

    def _check_price(self, second_criterion, start_stations, end_stations, start_routes, end_routes, bicycling_routes):
        # Look at bonus stations
        starts = [index for index, station in enumerate(start_stations) if not station["bonus"]]
        ends = [index for index, station in enumerate(end_stations) if station["bonus"]]
        if len(starts) > 0 and len(ends) > 0 and (len(starts) < len(start_stations) or len(ends) < len(end_stations)):
            all_indices = [s * len(start_stations) + e for (s, e) in zip(starts, ends)]
            start_sts = [start_stations[i] for i in starts]
            end_sts = [end_stations[i] for i in ends]
            start_rts = [start_routes[i] for i in starts]
            end_rts = [end_routes[i] for i in ends]
            bicycling_rts = [bicycling_routes[i] for i in all_indices]
            return self._optimize_route(second_criterion, start_sts, end_sts, start_rts, end_rts, bicycling_rts)
        else:
            return self._optimize_time(start_stations, end_stations, start_routes, end_routes, bicycling_routes)

    @staticmethod
    def _optimize_time(start_stations, end_stations, start_routes, end_routes, bicycling_routes):
        # Garde celui qui minimise le temps de parcours
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

    @staticmethod
    def _optimize_dist(start_stations, end_stations, start_routes, end_routes, bicycling_routes):
        # Garde celui qui minimise la distance parcourue
        dist_min = -1
        best_start = 0
        best_end = 0
        best_velib_route = None
        for start, start_station in enumerate(start_stations):
            dist_start = start_routes[start]["dist"]
            for end, end_station in enumerate(end_stations):
                dist_end = end_routes[end]["dist"]
                route = bicycling_routes.next_result()
                total_dist = route["dist"] + dist_start + dist_end
                if dist_min == -1 or total_dist < dist_min:
                    dist_min = total_dist
                    best_start = start
                    best_end = end
                    best_velib_route = route
        return best_start, best_end, best_velib_route

    @staticmethod
    def _optimize_walking(start_stations, end_stations, start_routes, end_routes, bicycling_routes):
        # Garde celui qui minimise le temps de marche
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
        return best_start, best_end, bicycling_routes[best_end * len(start_stations) + best_start]

    def get_price(self):
        price = 0
        subscription = self._ride.user.subscriptions["velib"]
        if subscription == NO_SUBSCRIPTION:
            # Si l'utilisateur n'a pas d'abonnement, il doit acheter son ticket
            price += ONE_TICKET_PRICE

        free_time = 45*60 if subscription == SUBSCRIPTION_45M else 30*60
        extra_time = self._modes_breakdown[BICYCLING_MODE] - free_time
        bonus = (not self._start_station["bonus"] and self._end_station["bonus"])
        if bonus:
            if extra_time > 0:
                extra_time -= 15
            elif subscription in [SUBSCRIPTION_45M, SUBSCRIPTION_30M]:
                price -= 0.5

        if extra_time > 0:
            price += 1
        if extra_time > 30:
            price += 2
        if extra_time > 60:
            price += 4 * ((extra_time - 60) // 30 + 1)

        # On suppose que tous les voyageurs ont le même forfait vélib et qu'ils sont en âge de faire du vélo
        return price * self._ride.travellers

    def get_discomfort(self):
        weather = self._ride.weather
        luggage = self._ride.luggage

        # Vérifier que les bagages du voyageur son bien compatible avec l'exercice du vélo
        # (sinon l'itinéraire VelibRoute n'aurait jamais dû ête simulé)
        for bag in luggage.keys():
            assert bag in [HANDBAG, BACKPACK]
        bags_data = (luggage[BACKPACK], luggage[HANDBAG])
        if luggage[BACKPACK] + luggage[HANDBAG] >= 4:
            bags_data = (4, 0)

        # Définition d'un barême approximatif qui traduit de degré d'inconfort ressenti (sur une échelle de 0 à 200)
        # Key = (veleur min exclue, valeur max inclue)
        rain_scores = {(-1, 0): 0, (0, 1): 25, (1, 5): 50, (5, 20): 75, (20, 50): 100, (50, 500): 200}
        snow_scores = {(-1, 0): 0, (0, 2): 25, (2, 4): 50, (4, 8): 75, (8, 30): 100, (30, 300): 200}
        wind_scores = {(-1, 0.5): 0, (0.5, 3): 15, (3, 8): 30, (8, 14): 45, (14, 20): 60, (20, 24): 75, (24, 28): 90,
                       (28, 33): 120, (33, 200): 200}
        temp_scores = {(-273, -10): 200, (-10, 0): 135, (0, 10): 45, (10, 20): 15, (20, 30): 0, (30, 40): 20,
                       (40, 50): 60, (50, 60): 180, (60, 150): 200}
        # Key = (nombre de sacs à dos, nombre de sacs à main)
        luggage_scores = {(0, 0): 0, (1, 0): 10, (0, 1): 15, (2, 0): 25, (1, 1): 25, (0, 2): 50, (3, 0): 55, (2, 1): 55,
                          (1, 2): 60, (0, 3): 95, (4, 0): 200}

        discomfort = 0
        for interval in rain_scores.keys():
            if interval[0] < weather["rain"] <= interval[1]:
                discomfort += rain_scores[interval]
                break
        for interval in snow_scores.keys():
            if interval[0] < weather["snow"] <= interval[1]:
                discomfort += snow_scores[interval]
                break
        for interval in wind_scores.keys():
            if interval[0] < weather["wind"] <= interval[1]:
                discomfort += wind_scores[interval]
                break
        for interval in temp_scores.keys():
            if interval[0] < weather["temperature"] <= interval[1]:
                discomfort += temp_scores[interval]
                break
        discomfort *= 3
        for key in luggage_scores.keys():
            if bags_data == key:
                discomfort += luggage_scores[tuple] * 8
                break
        return discomfort

    def display_route(self):
        print " - - - Itinéraire en Velib (recommandé selon vos critères) - - -"
        Route.display_route(self)
        print "Details :"
        print "  |"
        print "  | Marchez pendant {} min ({} m)".format(self._steps[0]["time"]/60.0, self._steps[0]["dist"])
        print "  |"
        print "  X Station Velib {}{}, à l'adresse {} ({} vélos disponibles)".format(
            self._start_station["name"],
            "(station bonus)" if self._start_station["bonus"] else "",
            self._start_station["address"],
            self._start_station["places"]
        )
        print "  |"
        print "  | Roulez à vélo pendant {} min ({} m)".format(self._steps[1]["time"]/60.0, self._steps[1]["dist"])
        print "  |"
        print "  X Station Velib {}{}, à l'adresse {} ({})".format(
            self._end_station["name"],
            "(station bonus)" if self._end_station["bonus"] else "",
            self._end_station["address"],
            self._end_station["places"]
        )
        print "  |"
        print "  | Marchez pendant {} min ({} m)".format(self._steps[2]["time"]/60.0, self._steps[2]["dist"])
        print "  |"
