# -*- coding: utf-8 -*-

import unittest
from core.ride import Ride
from core.user import User
from constants import BACKPACK, SUITCASE, BULKY
import time
from datetime import date, timedelta


class RideTest(unittest.TestCase):
    """ Test Case des méthodes du module 'ride'

    NB: Les types des paramêtres passés par l'utilisateur sont vérifiés lors de l'appel des fonctions principales
    de l'interface (définies dans la classe HowToGoSystem). Par conséquent, nous ne les revérifierons pas ici.

    """

    def setUp(self):
        self.user = User("Martin_dupond", "azerty", date.today() - timedelta(days=10000))
        self.ride = Ride(self.user, (48.832457, 2.327197), (48.859118, 2.369082), time.time())

    def test_constructor(self):

        self.assertEqual(self.ride.travellers, 1)
        self.assertEqual(len(self.ride.luggage), 0)
        self.assertEqual(self.ride.user, self.user)
        self.assertEqual(self.ride.preferences, self.user.preferences)
        self.assertAlmostEqual(self.ride.departure_time, time.time(), -1)
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

    def test_start_simulation(self):

        # Pas d'itinéraire possible
        self.ride.luggage = {BULKY: 1}
        self.user.driving_licence = False
        self.assertIsNone(self.ride.start_simulation())

        # Un seul itinéraire Autolib possible
        self.user.driving_licence = True
        # route = self.ride.start_simulation()

        # todo finish unittest