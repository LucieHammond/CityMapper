# -*- coding: utf-8 -*-

import unittest
from core.ride import Ride
from core.user import User
from routes.driving import AutolibRoute
from routes.transit import SubwayRoute
from constants import BACKPACK, SUITCASE, BULKY, FASTEST, SHORTEST, CHEAPEST, SIMPLEST, LESS_WALKING, LESS_PAINFUL, \
    WEATHER_IMPACT
import time
from datetime import date, timedelta


class RideTest(unittest.TestCase):
    """ Test Case des méthodes du module 'ride'

    NB: Les types des paramêtres passés par l'utilisateur sont vérifiés lors de l'appel des fonctions principales
    de l'interface (définies dans la classe HowToGoSystem). Par conséquent, nous ne les revérifierons pas ici.

    """

    def setUp(self):
        self.user = User("Martin_dupond", "azerty", date.today() - timedelta(days=10000))
        self.ride = Ride(self.user, (48.832457, 2.327197), (48.859118, 2.369082), time.time() + 10)

    def test_constructor(self):

        self.assertEqual(self.ride.user, self.user)
        self.assertAlmostEqual(self.ride.departure_time, time.time(), -2)
        self.assertEqual(self.ride.travellers, 1)
        self.assertEqual(len(self.ride.luggage.keys()), 0)
        self.assertEqual(self.ride.preferences, self.user.preferences)
        self.assertEqual(len(self.ride.weather.keys()), 4)
        for key in self.ride.weather:
            self.assertIn(key, ["temperature", "wind", "rain", "snow"])

    def test_luggage(self):

        self.ride.luggage = {BACKPACK: 1, SUITCASE: 1}
        self.assertEqual(len(self.ride.luggage), 2)

        with self.assertRaises(ValueError):
            self.ride.luggage = {"SADDLEBAG": 1}

        with self.assertRaises(ValueError):
            self.ride.luggage = {BACKPACK: 0.5}

    def test_travellers(self):

        self.ride.travellers = 10
        self.assertEqual(self.ride.travellers, 10)

        with self.assertRaises(ValueError):
            self.ride.travellers = 0

    def test_start_simulation(self):

        # Pas d'itinéraire possible
        self.ride.luggage = {BULKY: 1}
        self.user.driving_licence = False
        possible_routes, impossible_routes = self.ride.start_simulation()
        self.assertEqual(len(possible_routes), 0)
        self.assertEqual(len(impossible_routes), 3)
        self.assertEqual(impossible_routes[0]["mode"], "velib")
        self.assertEqual(impossible_routes[1]["mode"], "transit")
        self.assertEqual(impossible_routes[2]["mode"], "autolib")

        # Un seul itinéraire Autolib possible
        self.user.driving_licence = True
        possible_routes, impossible_routes = self.ride.start_simulation()
        self.assertEqual(len(possible_routes), 1)
        self.assertIsInstance(possible_routes[0], AutolibRoute)
        self.assertEqual(len(impossible_routes), 2)

        # Un seul itinéraire métro possible
        self.ride.luggage = {SUITCASE: 1}
        self.user.driving_licence = False
        possible_routes, impossible_routes = self.ride.start_simulation()
        self.assertEqual(len(possible_routes), 1)
        self.assertIsInstance(possible_routes[0], SubwayRoute)
        self.assertEqual(len(impossible_routes), 2)

        # Deux itinéraires Autolib et métro possibles
        self.user.driving_licence = True
        possible_routes, impossible_routes = self.ride.start_simulation()
        self.assertEqual(len(possible_routes), 2)
        self.assertEqual(len(impossible_routes), 1)
        self.assertEqual(impossible_routes[0]["mode"], "velib")

        # Deux itinéraires Vélib et métro possibles
        self.ride.luggage = {BACKPACK: 1}
        self.user.driving_licence = False
        possible_routes, impossible_routes = self.ride.start_simulation()
        self.assertEqual(len(possible_routes), 2)
        self.assertEqual(len(impossible_routes), 1)
        self.assertEqual(impossible_routes[0]["mode"], "autolib")

        # Tous les itinéraires possibles (critère = temps)
        self.user.driving_licence = True
        self.user.preferences = {FASTEST: 5, SHORTEST: 0, CHEAPEST: 0, LESS_WALKING: 0, SIMPLEST: 0, WEATHER_IMPACT: 0,
                                 LESS_PAINFUL: 0}
        possible_routes, impossible_routes = self.ride.start_simulation()
        self.assertEqual(len(possible_routes), 3)
        self.assertEqual(len(impossible_routes), 0)
        self.assertLessEqual(possible_routes[0].time, possible_routes[1].time)
        self.assertLessEqual(possible_routes[1].time, possible_routes[2].time)

        # Tous les itinéraires possibles (critère = prix)
        self.user.preferences = {FASTEST: 0, SHORTEST: 0, CHEAPEST: 5, LESS_WALKING: 0, SIMPLEST: 0, WEATHER_IMPACT: 0,
                                 LESS_PAINFUL: 0}
        possible_routes, impossible_routes = self.ride.start_simulation()
        self.assertEqual(len(possible_routes), 3)
        self.assertEqual(len(impossible_routes), 0)
        self.assertLessEqual(possible_routes[0].price, possible_routes[1].price)
        self.assertLessEqual(possible_routes[1].price, possible_routes[2].price)
