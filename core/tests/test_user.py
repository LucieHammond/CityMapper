# -*- coding: utf-8 -*-

import unittest
from core.user import User
from constants import FASTEST, SHORTEST, CHEAPEST, SIMPLEST, LESS_PAINFUL, WEATHER_IMPACT, LESS_WALKING, \
    VELIB_NO_SUBSCRIPTION, VELIB_SUBSCRIPTION_30M, \
    AUTOLIB_PRET_A_ROULER, AUTOLIB_PREMIUM, \
    SUBWAY_NO_TITLE, SUBWAY_NAVIGO_SUBSCRIPTION
from datetime import date, timedelta


class UserTest(unittest.TestCase):
    """ Test Case des méthodes du module 'user'

    NB: Les types des paramêtres passés par l'utilisateur sont vérifiés lors de l'appel des fonctions principales
    de l'interface (définies dans la classe HowToGoSystem). Par conséquent, nous ne les revérifierons pas ici.

    """

    def test_constructor(self):

        with self.assertRaises(ValueError):
            User("user1", "00000", date.today() + timedelta(days=1))

        username = "user2"
        password = "11111"

        user_2 = User("user2", "11111", date.today() - timedelta(days=7500))
        self.assertEqual(user_2.username, username)
        self.assertEqual(user_2.password, password)
        self.assertEqual(user_2.age, 20)

        self.assertEqual(user_2.subscriptions.keys(), ["velib", "autolib", "subway"])
        self.assertEqual(user_2.subscriptions["velib"], VELIB_NO_SUBSCRIPTION)
        self.assertEqual(user_2.subscriptions["autolib"], AUTOLIB_PRET_A_ROULER)
        self.assertEqual(user_2.subscriptions["subway"], SUBWAY_NO_TITLE)
        self.assertTrue(user_2.driving_licence)

        self.assertEqual(sorted(user_2.preferences.keys()),
                         [CHEAPEST, FASTEST, LESS_PAINFUL, LESS_WALKING, SHORTEST, SIMPLEST, WEATHER_IMPACT])
        for value in user_2.preferences.values():
            self.assertIn(value, range(0, 6))

    def test_subscriptions(self):

        user_3 = User("user3", "22222", date.today() - timedelta(days=7500))
        user_3.set_subscriptions_infos(VELIB_SUBSCRIPTION_30M, AUTOLIB_PREMIUM, SUBWAY_NAVIGO_SUBSCRIPTION)

        self.assertEqual(user_3.subscriptions["velib"], VELIB_SUBSCRIPTION_30M)
        self.assertEqual(user_3.subscriptions["autolib"], AUTOLIB_PREMIUM)
        self.assertEqual(user_3.subscriptions["subway"], SUBWAY_NAVIGO_SUBSCRIPTION)

        with self.assertRaises(ValueError):
            user_3.set_subscriptions_infos("NONEXISTENT_SUBSCRIPTION", AUTOLIB_PRET_A_ROULER, SUBWAY_NO_TITLE)

    def test_preferences(self):

        user_4 = User("user4", "33333", date.today() - timedelta(days=7500))

        with self.assertRaises(ValueError):
            user_4.preferences = {FASTEST: 4, SHORTEST: 0}

        with self.assertRaises(ValueError):
            user_4.preferences = {FASTEST: 4, SHORTEST: 0, CHEAPEST: 3, SIMPLEST: 2, "OTHER": 5, LESS_WALKING: 1}

        with self.assertRaises(ValueError):
            user_4.preferences = {FASTEST: 12, SHORTEST: -2, CHEAPEST: 7, SIMPLEST: 5, WEATHER_IMPACT: 8,
                                  LESS_PAINFUL: 23, LESS_WALKING: 0}
