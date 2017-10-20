# -*- coding: utf-8 -*-

from route import Route
from webservice.velib import Velib
from webservice.directions import Directions
from core.tasks import TasksManager
from constants import WALKING_MODE, BICYCLING_MODE, FASTEST, SHORTEST, LESS_WALKING, CHEAPEST, BACKPACK, HANDBAG, \
    VELIB_SUBSCRIPTION_30M, VELIB_SUBSCRIPTION_45M, VELIB_NO_SUBSCRIPTION
import time

ONE_HOUR = 3600
ONE_TICKET_PRICE = 1.70


class VelibRoute(Route):
    """ Itinéraire en Vélib correspondant au trajet demandé """

    def __init__(self, ride):
        Route.__init__(self, ride)
        # 2 caractéristiques spécifiques à l'itinéraire en Vélib : station de départ et station d'arrivée
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

        Le calcul se fait grâce aux données récupérées depuis les APIs Open Data Velib et Google Map
        Met à jour les paramêtres de l'objet (initialisés à None pour la plupart) avec l'itinéraire calculé
        """

        velib = Velib()
        directions = Directions()
        ride = self._ride

        # Critères de préférence pour la différentiation des itinéraires similaires
        search_criterion, check_price = self._define_search_criteria()

        # On va vérifier les places displonibles uniquement si le départ a lieu dans moins d'une heure
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

        if len(start_stations) == 0 or len(end_stations) == 0:
            return False

        # Calcule les itinéraires à vélo pour toutes les combinaisons possibles (9 appels au maximum)
        bicycling_routes = TasksManager()
        for start_station in start_stations:
            for end_station in end_stations:
                bicycling_routes.new_task(target=directions.get_from_api,
                                          args=(start_station["position"], end_station["position"], BICYCLING_MODE))

        # Compare les itinéraires possibles et renvoie le meilleur compte tenu des préférences de l'utilisateur
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
        return True

    def _define_search_criteria(self):
        """ Analyse les préférences de l'utilisateur pour déterminer le critère de sélection le plus adapté
        Le critère est cherché parmi ceux qui sont pertinents pour différencier deux trajets similaires en Vélib

        :return:
        - critère de recherche préféré parmi FASTEST, LESS_WALKING, SHORTEST
        - booléen indiquant si on veut optimiser le prix avant la comparaison (pour éliminer peut-être des solutions)

        """
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
        """  Renvoie le meilleur itinéraire suivant le critère d'optimisation passé en paramêtre

        :param criterion: critère d'optimisation
        :param start_sts: liste des stations de départ possibles (3)
        :param end_sts: liste des stations d'arrivée possibles (3)
        :param start_rts: liste des chemins à pied associés aux stations de départ (3)
        :param end_rts: liste des chemins à pied associés aux stations d'arrivée (3)
        :param bicycling_rts: liste des itinéraires en vélo d'une station à un autre (3 x 3)
        :return: index des meilleures stations de départ et d'arrivée, itinéraire en vélo entre les deux

        """
        if criterion == FASTEST:
            return self._optimize_time(start_sts, end_sts, start_rts, end_rts, bicycling_rts)
        elif criterion == SHORTEST:
            return self._optimize_dist(start_sts, end_sts, start_rts, end_rts, bicycling_rts)
        else:
            return self._optimize_walking(start_sts, end_sts, start_rts, end_rts, bicycling_rts.results_list())

    def _check_price(self, second_criterion, start_stations, end_stations, start_routes, end_routes, bicycling_routes):
        """ Sélectionner éventuellement les stations en cas de différence de prix constatée (stations bonus) """

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
            # Si les bonus ne permettent pas de différencier les stations, alors le prix se joue sur le temps passé
            return self._optimize_time(start_stations, end_stations, start_routes, end_routes, bicycling_routes)

    @staticmethod
    def _optimize_time(start_stations, end_stations, start_routes, end_routes, bicycling_routes):
        """ Garde l'itinéraire celui qui minimise le temps de parcours """
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
        """ Garde l'itinéraire qui minimise la distance parcourue """
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
        return best_start, best_end, bicycling_routes[best_end * len(start_stations) + best_start]

    def _compute_price(self):
        """ Calcule le prix exact de l'itinéraire finalement choisi """

        price = 0
        subscription = self._ride.user.subscriptions["velib"]
        if subscription == VELIB_NO_SUBSCRIPTION:
            # Si l'utilisateur n'a pas d'abonnement, il doit acheter son ticket
            price += ONE_TICKET_PRICE

        free_time = 45*60 if subscription == VELIB_SUBSCRIPTION_45M else 30*60
        extra_time = self._modes_breakdown[BICYCLING_MODE] - free_time
        bonus = (not self._start_station["bonus"] and self._end_station["bonus"])
        if bonus:
            # Les stations bonus font gagner 15 min, reportables si abonnement (soit 0.5€ la première demi-heure extra)
            if extra_time > 0:
                extra_time -= 15*60
            elif subscription in [VELIB_SUBSCRIPTION_45M, VELIB_SUBSCRIPTION_30M]:
                price -= 0.5

        extra_time /= 60.0  # Mettre en minutes
        if extra_time > 0:
            price += 1
        if extra_time > 30:
            price += 2
        if extra_time > 60:
            price += 4 * ((extra_time - 60) // 30 + 1)

        # On suppose que tous les voyageurs ont le même forfait vélib et qu'ils sont en âge de faire du vélo
        return price * self._ride.travellers

    def _compute_difficulty(self):
        """ Calcule le degré d'inconfort lié à la charge portée pour l'itinéraire finalement choisi """

        luggage = self._ride.luggage

        # Vérifier que les bagages du voyageur sont bien compatible avec l'exercice du vélo
        for bag in luggage.keys():
            assert bag in [HANDBAG, BACKPACK]
        backpacks = luggage[BACKPACK] if BACKPACK in luggage.keys() else 0
        handbags = luggage[HANDBAG] if HANDBAG in luggage.keys() else 0
        bags_data = (backpacks, handbags) if backpacks + handbags < 4 else (4, 0)

        # Définition d'un barême approximatif qui traduit de degré d'inconfort ressenti (sur une échelle de 0 à 200)
        # Key = (nombre de sacs à dos, nombre de sacs à main)
        luggage_scores = {(0, 0): 0, (1, 0): 10, (0, 1): 15, (2, 0): 25, (1, 1): 25, (0, 2): 50, (3, 0): 55, (2, 1): 55,
                          (1, 2): 60, (0, 3): 95, (4, 0): 200}

        for key in luggage_scores.keys():
            if bags_data == key:
                return luggage_scores[key]

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
