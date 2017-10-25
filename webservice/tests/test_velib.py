# -*- coding: utf-8 -*-

import unittest
from webservice.velib import Velib


class WeatherTest(unittest.TestCase):
    """ Test Case des méthodes du module 'velib' """

    def test_api(self):

        velib = Velib()
        point = (48.852259, 2.369495)

        data_start = velib.get_from_api(point, True)
        data_end = velib.get_from_api(point, False)
        data_postponed = velib.get_from_api(point, True, False)

        self.assertIsInstance(data_start, list)
        self.assertLessEqual(len(data_start), 3)
        self.assertLessEqual(len(data_end), 3)
        self.assertEqual(sorted(data_start[0].keys()), ["address", "bonus", "name", "places", "position"])
        self.assertEqual(sorted(data_end[0].keys()), ["address", "bonus", "name", "places", "position"])
        self.assertEqual(sorted(data_postponed[0].keys()), ["address", "bonus", "name", "position"])

        self.assertIsInstance(data_start[0]["bonus"], bool)
        self.assertGreater(data_start[0]["places"], 0)
        self.assertGreater(data_end[0]["places"], 0)
