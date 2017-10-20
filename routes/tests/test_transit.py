# -*- coding: utf-8 -*-

import unittest
from routes.transit import SubwayRoute, ONE_TICKET_PRICE, TEN_TICKETS_REDUCED_PRICE
from core.ride import Ride
from core.user import User
from constants import FASTEST, SHORTEST, CHEAPEST, LESS_WALKING, SIMPLEST, WEATHER_IMPACT, LESS_PAINFUL, \
    VELIB_NO_SUBSCRIPTION, AUTOLIB_PRET_A_ROULER, SUBWAY_TICKETS_REDUCED, SUBWAY_NAVIGO_SUBSCRIPTION, \
    HANDBAG, SUITCASE
from datetime import date, timedelta
import time
from math import sqrt


def _distance_between(position1, position2):
    return sqrt((position1[0] - position2[0])**2 + (position1[1] - position2[1])**2)


class TransitRouteTest(unittest.TestCase):
    """ Test Case des méthodes du module 'driving' """

    def setUp(self):
        user = User("Martin_dupond", "azerty", date.today() - timedelta(days=10000))
        self.ride = Ride(user, (48.829728, 2.356414), (48.885599, 2.343342), time.time() + 60)
        self.route = SubwayRoute(self.ride)
        self.success = self.route.calculate_route()

    def test_calculate_route(self):

        self.assertTrue(self.success)

        # Vérifie la cohérence des stations trouvées
        self.assertIsInstance(self.route.stations_list, list)
        self.assertEqual(len(self.route.stations_list), len(self.route.steps) - 1)
        for station in self.route.stations_list:
            self.assertEqual(sorted(station.keys()), ["line", "name", "position"])

        # Vérifie la cohérence des données détaillées de l'itinéraire
        self.assertIsNotNone(self.route.steps)
        self.assertGreaterEqual(len(self.route.steps), 3)
        self.assertLessEqual(self.route.walking_time, self.route.time)
        self.assertGreaterEqual(self.route.distance, _distance_between(self.ride.start, self.ride.end))
        self.assertLessEqual(self.route.transfers_nb, len(self.route.stations_list))

        # Comparaisons des résultats trouvés par critère de recherche
        # --- par défault c'était le plus rapide
        time_fastest = self.route.time
        transfers_fastest = self.route.transfers_nb
        walking_fastest = self.route.walking_time

        # --- le moins de marche
        self.ride.preferences = {FASTEST: 1, SHORTEST: 0, CHEAPEST: 3, LESS_WALKING: 5, SIMPLEST: 2, WEATHER_IMPACT: 6,
                                 LESS_PAINFUL: 4}
        self.route = SubwayRoute(self.ride)
        self.route.calculate_route()
        self.assertGreaterEqual(self.route.time, time_fastest)
        self.assertLessEqual(self.route.walking_time, walking_fastest)

        # --- le moins de correspondances
        self.ride.preferences = {FASTEST: 5, SHORTEST: 0, CHEAPEST: 3, LESS_WALKING: 1, SIMPLEST: 6, WEATHER_IMPACT: 0,
                                 LESS_PAINFUL: 4}
        self.route = SubwayRoute(self.ride)
        self.route.calculate_route()
        self.assertGreaterEqual(self.route.time, time_fastest)
        self.assertLessEqual(self.route.transfers_nb, transfers_fastest)

    def test_price(self):

        # --- Aucun forfait
        self.assertEqual(self.route.price, ONE_TICKET_PRICE)

        # --- Pass Navigo illimité
        self.ride.user.set_subscriptions_infos(VELIB_NO_SUBSCRIPTION, AUTOLIB_PRET_A_ROULER, SUBWAY_NAVIGO_SUBSCRIPTION)
        self.route = SubwayRoute(self.ride)
        self.route.calculate_route()
        self.assertEqual(self.route.price, 0)

        # --- Carnet de tickets tarif réduit
        self.ride.user.set_subscriptions_infos(VELIB_NO_SUBSCRIPTION, AUTOLIB_PRET_A_ROULER, SUBWAY_TICKETS_REDUCED)
        self.route = SubwayRoute(self.ride)
        self.route.calculate_route()
        self.assertEqual(self.route.price, round(TEN_TICKETS_REDUCED_PRICE/10.0,2))

    def test_weather_impact(self):
        self.assertGreaterEqual(self.route.weather_impact, -150)
        self.assertLessEqual(self.route.weather_impact, 1500)

    def test_difficulty(self):
        self.assertEqual(self.route.difficulty, 0)

        self.ride.luggage = {SUITCASE: 1, HANDBAG: 1}
        self.route = SubwayRoute(self.ride)
        self.route.calculate_route()
        self.assertEqual(self.route.difficulty, 65)

if __name__ == "__main__":
    unittest.main()