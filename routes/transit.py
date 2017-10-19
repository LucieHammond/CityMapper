# -*- coding: utf-8 -*-

from route import Route
from webservice.directions import Directions
from core.tasks import TasksManager
from constants import TRANSIT_MODE, WALKING_MODE, FASTEST, LESS_WALKING, SIMPLEST, \
    SUBWAY_NAVIGO_SUBSCRIPTION, SUBWAY_TICKETS_BOOK, SUBWAY_TICKETS_REDUCED, BACKPACK, HANDBAG, SUITCASE

ONE_TICKET_PRICE = 1.90
TEN_TICKETS_PRICE = 14.90
TEN_TICKETS_REDUCED_PRICE = 7.45


class SubwayRoute(Route):

    def __init__(self, ride):
        Route.__init__(self, ride)
        self._stations_list = None

    @property
    def stations_list(self):
        return self._stations_list

    def calculate_route(self):
        """ Calcule l'itinéraire exact le plus adapté aux préférences de l'utilisateur
        L'itinéraire est récupéré depuis l'API Directions de Google Maps
        """

        directions = Directions()
        ride = self._ride

        # Critères de préférence pour la différentiation des itinéraires similaires
        search_criterion = self._define_search_criteria()
        routing_pref = {FASTEST: None, LESS_WALKING: "less_walking", SIMPLEST: "fewer_transfers"}[search_criterion]

        tm = TasksManager()
        tm.new_task(target=directions.get_from_api,
                    args=(ride.start, ride.end, TRANSIT_MODE, ride.departure_time, routing_pref))
        route = tm.next_result()

        # On peut maintenant définir les caractéristiques de la route trouvée
        self._time = route["main"]["time"]
        self._dist = route["main"]["dist"]

        transfers_nb = 0
        self._stations_list = list()
        self._steps = list()
        last_station = None
        for step in route["steps"]:
            self._steps.append(step)
            if step["mode"] == TRANSIT_MODE:
                start_station = step["details"]["start"]
                end_station = step["details"]["end"]

                if not last_station or last_station["name"] != start_station["name"]:
                    transfers_nb += 1
                if not last_station or last_station["position"] != start_station["position"]:
                    start_station["line"] = step["details"]["line"]
                    self._stations_list.append(start_station)

                end_station["line"] = step["details"]["line"]
                self._stations_list.append(end_station)
                last_station = end_station
                transfers_nb += 1

        assert len(self._stations_list) == len(self._steps) - 1
        self._transfers_nb = transfers_nb

        walking_time = sum([step["time"] for step in route["steps"] if step["mode"] == WALKING_MODE])
        transit_time = sum([step["time"] for step in route["steps"] if step["mode"] == TRANSIT_MODE])
        self._modes_breakdown = {WALKING_MODE: walking_time, TRANSIT_MODE: transit_time}
        self._walking_time = walking_time

        return True

    def _define_search_criteria(self):
        """ Analyse les préférences de l'utilisateur pour déterminer le critère de sélection le plus adapté
        Le critère est cherché parmi ceux qui sont pertinents pour différencier deux trajets en transports en commun

        :return: critère de recherche préféré parmi FASTEST, LESS_WALKING, SIMPLEST

        """
        preferences = self._ride.preferences

        relevant_criteria = [FASTEST, LESS_WALKING, SIMPLEST]
        best_criterion = FASTEST
        grade = 5
        while grade >= 0:
            criteria = [c for c, v in preferences.items() if v == grade and c in relevant_criteria]
            if len(criteria) > 1:
                best_criterion = FASTEST if FASTEST else LESS_WALKING
                break
            elif len(criteria) == 1:
                best_criterion = criteria[0]
                break
            else:
                grade -= 1

        return best_criterion

    def _compute_price(self):
        """ Calcule le prix exact de l'itinéraire finalement choisi """

        if self._modes_breakdown[TRANSIT_MODE] == 0:
            return 0

        subscription = self._ride.user.subscriptions["subway"]
        if subscription == SUBWAY_NAVIGO_SUBSCRIPTION:
            return 0
        elif subscription == SUBWAY_TICKETS_BOOK:
            return TEN_TICKETS_PRICE / 10.0
        elif subscription == SUBWAY_TICKETS_REDUCED:
            return TEN_TICKETS_REDUCED_PRICE / 10.0
        else:
            return ONE_TICKET_PRICE

    def _compute_difficulty(self):
        """ Calcule degré d'inconfort lié à la charge portée par le voyageur """

        luggage = self._ride.luggage

        # Vérifier que les bagages du voyageur ne sont pas trop fragiles ou encombrants pour être transporté en métro
        nb_bags = 0
        for bag in luggage.keys():
            assert bag in [BACKPACK, HANDBAG, SUITCASE]
            nb_bags += luggage[bag]

        # Définition d'un barême approximatif qui traduit de degré d'inconfort ressenti (sur une échelle de 0 à 200)
        luggage_scores = {BACKPACK: 10, HANDBAG: 10, SUITCASE: 50}
        difficulty = sum([luggage_scores[bag] * nb for bag, nb in luggage.items()])
        difficulty += 10 * max([0, nb_bags - 1])

        return difficulty
