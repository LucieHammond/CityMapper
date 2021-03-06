# -*- coding: utf-8 -*-

import unittest
from routes.bicycling import VelibRoute, ONE_TICKET_PRICE
from core.ride import Ride
from core.user import User
from constants import FASTEST, SHORTEST, CHEAPEST, LESS_WALKING, SIMPLEST, WEATHER_IMPACT, LESS_PAINFUL, \
    VELIB_SUBSCRIPTION_30M, VELIB_SUBSCRIPTION_45M, AUTOLIB_PRET_A_ROULER, SUBWAY_NO_TITLE, \
    BACKPACK, HANDBAG
from datetime import date, timedelta
import time
from math import sqrt


def _distance_between(position1, position2):
    return sqrt((position1[0] - position2[0])**2 + (position1[1] - position2[1])**2)


class VelibRouteTest(unittest.TestCase):
    """ Test Case des méthodes du module 'bicycling' """

    def setUp(self):
        user = User("Martin_dupond", "azerty", date.today() - timedelta(days=10000))
        self.ride = Ride(user, (48.805363, 2.378078), (48.885599, 2.343342), time.time() + 60)
        self.route = VelibRoute(self.ride)
        self.success = self.route.calculate_route()

    def test_calculate_route(self):

        self.assertTrue(self.success)

        # Vérifie la cohérence des stations trouvées
        self.assertIsNotNone(self.route.start_station)
        self.assertIsNotNone(self.route.end_station)
        self.assertEqual(sorted(self.route.start_station.keys()), ["address", "bonus", "name", "places", "position"])
        self.assertEqual(sorted(self.route.end_station.keys()), ["address", "bonus", "name", "places", "position"])
        self.assertIsInstance(self.route.start_station["bonus"], bool)
        self.assertIsInstance(self.route.end_station["bonus"], bool)
        self.assertLessEqual(_distance_between(self.ride.start, self.route.start_station["position"]), 900)
        self.assertLessEqual(_distance_between(self.ride.end, self.route.end_station["position"]), 900)

        # Vérifie la cohérence des données détaillées de l'itinéraire
        self.assertIsNotNone(self.route.steps)
        self.assertEqual(len(self.route.steps), 3)
        self.assertEqual(self.route.walking_time, self.route.steps[0]["time"] + self.route.steps[2]["time"])
        self.assertLessEqual(self.route.walking_time, self.route.time)
        self.assertGreaterEqual(self.route.distance, _distance_between(self.ride.start, self.ride.end))
        self.assertEqual(self.route.transfers_nb, 0)

        # Comparaisons des résultats trouvés par critère de recherche
        # --- par défault c'était le plus rapide
        time_fastest = self.route.time
        dist_fastest = self.route.distance
        walking_fastest = self.route.walking_time

        # --- le moins de marche
        self.ride.user.preferences = {FASTEST: 1, SHORTEST: 0, CHEAPEST: 3, LESS_WALKING: 5, SIMPLEST: 2,
                                      WEATHER_IMPACT: 5, LESS_PAINFUL: 4}
        self.route = VelibRoute(self.ride)
        self.route.calculate_route()
        self.assertGreaterEqual(self.route.time, time_fastest)
        self.assertLessEqual(self.route.walking_time, walking_fastest)

        # --- le plus court en distance
        self.ride.user.preferences = {FASTEST: 0, SHORTEST: 5, CHEAPEST: 3, LESS_WALKING: 1, SIMPLEST: 2,
                                      WEATHER_IMPACT: 5, LESS_PAINFUL: 4}
        self.route = VelibRoute(self.ride)
        self.route.calculate_route()
        self.assertGreaterEqual(self.route.time, time_fastest)
        self.assertLessEqual(self.route.distance, dist_fastest)

    def test_price(self):
        # Ici, le trajet à vélo fait entre 45min et 60min et a pour arrivée une station bonus (départ = non bonus)

        # --- Aucun forfait
        self.assertEqual(self.route.price, ONE_TICKET_PRICE + 1)

        # --- Forfait 30 min
        self.ride.user.set_subscriptions_infos(VELIB_SUBSCRIPTION_30M, AUTOLIB_PRET_A_ROULER, SUBWAY_NO_TITLE)
        self.route = VelibRoute(self.ride)
        self.route.calculate_route()
        self.assertEqual(self.route.price, 1)

        # --- Forfait 45 min
        self.ride.user.set_subscriptions_infos(VELIB_SUBSCRIPTION_45M, AUTOLIB_PRET_A_ROULER, SUBWAY_NO_TITLE)
        self.route = VelibRoute(self.ride)
        self.route.calculate_route()
        self.assertEqual(self.route.price, 0)

    def test_weather_impact(self):
        self.assertGreaterEqual(self.route.weather_impact, -150)
        self.assertLessEqual(self.route.weather_impact, 1500)

    def test_difficulty(self):
        self.assertEqual(self.route.difficulty, 0)

        self.ride.luggage = {BACKPACK: 1, HANDBAG: 1}
        self.route = VelibRoute(self.ride)
        self.route.calculate_route()
        self.assertEqual(self.route.difficulty, 25)
