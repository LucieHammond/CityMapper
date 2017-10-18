# -*- coding: utf-8 -*-

import unittest
from routes.bicycling import VelibRoute
from core.ride import Ride
from core.user import User
from constants import FASTEST, SHORTEST, CHEAPEST, EASIEST, NICEST, LESS_WALKING
from datetime import date, timedelta
import time
from math import sqrt


def _distance_between(position1, position2):
    return sqrt((position1[0] - position2[0])**2 + (position1[1] - position2[1])**2)


class VelibRouteTest(unittest.TestCase):

    def setUp(self):
        user = User("Martin_dupond", "azerty", date.today() - timedelta(days=10000))
        self.ride = Ride(user, (48.832457, 2.327197), (48.859118, 2.369082), time.time())
        self.route = VelibRoute(self.ride)
        self.route.calculate_route()

    def test_calculate_route(self):

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
        self.assertEqual(self.route.transfers_nb, 2)

        # Comparaisons des résultats trouvés par critère de recherche
        time_fastest = self.route.time
        dist_fastest = self.route.distance
        walking_fastest = self.route.walking_time

        self.ride.preferences = {FASTEST: 4, SHORTEST: 0, CHEAPEST: 3, EASIEST: 2, NICEST: 1, LESS_WALKING: 5}
        self.route.calculate_route()
        self.assertGreaterEqual(self.route.time, time_fastest)
        print self.route.time, time_fastest
        self.assertLessEqual(self.route.walking_time, walking_fastest)
        print self.route.walking_time, walking_fastest

        self.ride.preferences = {FASTEST: 4, SHORTEST: 5, CHEAPEST: 3, EASIEST: 2, NICEST: 0, LESS_WALKING: 1}
        self.route.calculate_route()
        self.assertGreaterEqual(self.route.time, time_fastest)
        self.assertLessEqual(self.route.distance, dist_fastest)

    def test_price(self):
        pass

    def test_discomfort(self):
        pass

if __name__ == "__main__":
    unittest.main()