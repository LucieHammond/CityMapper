# -*- coding: utf-8 -*-

import unittest
from core.system import HowToGoSystem
from datetime import date
import time
from constants import VELIB_SUBSCRIPTION_30M, AUTOLIB_PREMIUM, SUBWAY_NAVIGO_SUBSCRIPTION, FASTEST, SHORTEST, CHEAPEST,\
    SIMPLEST, LESS_WALKING, LESS_PAINFUL, WEATHER_IMPACT, BACKPACK, SUITCASE


class SystemTest(unittest.TestCase):
    """ Test Case des méthodes de l'interface 'HowToGoSystem' """

    def setUp(self):
        self.system = HowToGoSystem()

    def test_sign(self):
        self.assertIsNone(self.system.current_user)

        # Sign Up
        result = self.system.sign_up('Hamza', 'azerty', date(date.today().year + 1, 01, 01))
        self.assertFalse(result["success"])

        result = self.system.sign_up('Hamza', 'azerty', date(1994, 01, 01))
        self.assertTrue(result["success"])
        self.assertIsNotNone(self.system.current_user)

        result = self.system.sign_up('Hamza', 'azerty', date(1994, 01, 01))
        self.assertFalse(result["success"])

        # Sign Out
        result = self.system.sign_out()
        self.assertTrue(result["success"])
        self.assertIsNone(self.system.current_user)

        # Sign In
        result = self.system.sign_in("Simo", "azerty")
        self.assertFalse(result["success"])

        result = self.system.sign_in("Hamza", "qwerty")
        self.assertFalse(result["success"])
        self.assertIsNone(self.system.current_user)

        result = self.system.sign_in("Hamza", "azerty")
        self.assertTrue(result["success"])
        self.assertIsNotNone(self.system.current_user)

    def test_profile_settings(self):
        self.system.sign_up('Hamza', 'azerty', date(1994, 01, 01))

        prefs = {FASTEST: 5, SHORTEST: 0, CHEAPEST: 3, LESS_WALKING: 2, SIMPLEST: 0, WEATHER_IMPACT: 1, LESS_PAINFUL: 1}
        result = self.system.set_profile_settings(VELIB_SUBSCRIPTION_30M, AUTOLIB_PREMIUM, SUBWAY_NAVIGO_SUBSCRIPTION,
                                                  True, prefs)
        self.assertTrue(result["success"])
        self.assertTrue(self.system.current_user.driving_licence)
        self.assertEqual(self.system.current_user.preferences, prefs)

        result = self.system.set_profile_settings("wrong_subscription", AUTOLIB_PREMIUM, SUBWAY_NAVIGO_SUBSCRIPTION,
                                                  True, prefs)
        self.assertFalse(result["success"])

        with self.assertRaises(AssertionError):
            self.system.set_profile_settings(VELIB_SUBSCRIPTION_30M, AUTOLIB_PREMIUM, SUBWAY_NAVIGO_SUBSCRIPTION,
                                             'True', prefs)

    def test_ride(self):
        self.system.sign_up('Hamza', 'azerty', date(1994, 01, 01))
        self.assertIsNone(self.system.current_ride)

        # New ride
        result = self.system.new_ride('3 rue Joliot Curie, Gif-sur-Yvette', '5 avenue Sully-Prudhomme, Châtenay',
                                      time.time() - 10)
        self.assertFalse(result["success"])

        result = self.system.new_ride('3 rue Joliot Curie, Gif-sur-Yvette', '5 avenue Sully-Prudhomme, Châtenay',
                                      time.time() + 50)
        self.assertTrue(result["success"])
        self.assertIsNotNone(self.system.current_ride)

        result = self.system.new_ride('@ 48.832457, 2.327197', '@ 48.859118, 2.369082', time.time() + 50)
        self.assertTrue(result["success"])
        self.assertIsNotNone(self.system.current_ride)

        # Set ride precisions
        result = self.system.set_ride_precisions(0, {})
        self.assertFalse(result["success"])

        with self.assertRaises(AssertionError):
            self.system.set_ride_precisions(1, [BACKPACK, SUITCASE])

        result = self.system.set_ride_precisions(3, {BACKPACK: 1, SUITCASE: 1})
        self.assertTrue(result["success"])

        # Cancel ride
        result = self.system.cancel_ride()
        self.assertTrue(result["success"])
        self.assertIsNone(self.system.current_ride)

    def test_start_calculation(self):
        self.system.sign_up('Hamza', 'azerty', date(1994, 01, 01))
        self.system.new_ride('@ 48.832457, 2.327197', '@ 48.859118, 2.369082', time.time() + 50)
        result = self.system.start_calculation()
        self.assertTrue(result["success"])
        self.assertIn("possible_routes", result.keys())
        self.assertIn("unsuitable_routes", result.keys())
