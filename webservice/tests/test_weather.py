# -*- coding: utf-8 -*-

import unittest
from webservice.weather import Weather
import time


class WeatherTest(unittest.TestCase):
    """ Test Case des méthodes du module 'weather' """

    def test_api(self):

        weather = Weather()
        data = weather.get_from_api()
        self.assertIsInstance(data, dict)
        self.assertEqual(sorted(data.keys()), ["rain", "snow", "temperature", "wind"])
        for value in data.values():
            self.assertIsInstance(value, (float, int))
        self.assertGreaterEqual(data["rain"], 0)
        self.assertGreaterEqual(data["snow"], 0)
        self.assertGreaterEqual(data["wind"], 0)
        self.assertGreaterEqual(data["temperature"], -273.15)

        data2 = data = weather.get_from_api(time.time())
        self.assertEqual(data, data2)
