# -*- coding: utf-8 -*-

import unittest
from webservice.autolib import Autolib


class WeatherTest(unittest.TestCase):
    """ Test Case des méthodes du module 'velib' """

    def test_api(self):

        autolib = Autolib()
        point = (48.852259, 2.369495)

        data_start = autolib.get_from_api(point, True)
        data_end = autolib.get_from_api(point, False)
        data_postponed = autolib.get_from_api(point, True, False)

        self.assertIsInstance(data_start, list)
        self.assertLessEqual(len(data_start), 3)
        self.assertLessEqual(len(data_end), 3)
        self.assertEqual(sorted(data_start[0].keys()), ["address", "geo_point", "places", "public_name"])
        self.assertEqual(sorted(data_end[0].keys()), ["address", "geo_point", "places", "public_name"])
        self.assertEqual(sorted(data_postponed[0].keys()), ["address", "geo_point", "public_name"])

        self.assertGreater(data_start[0]["places"], 0)
        self.assertGreater(data_end[0]["places"], 0)
