# -*- coding: utf-8 -*-

import unittest
from webservice.directions import Directions
from constants import WALKING_MODE, BICYCLING_MODE, DRIVING_MODE, TRANSIT_MODE
from datetime import datetime, timedelta
import time


class WeatherTest(unittest.TestCase):
    """ Test Case des méthodes du module 'directions' """

    def test_api(self):

        directions = Directions()
        start = (48.866968, 2.364910)
        end = (48.852259, 2.369495)
        date = datetime.now() + timedelta(days=1)
        tomorrow_day = time.mktime(datetime(date.year, date.month, date.day, 16, 30).timetuple())
        tomorrow_night = time.mktime(datetime(date.year, date.month, date.day, 3, 0).timetuple())

        data_walking = directions.get_from_api(start, end, WALKING_MODE)
        data_bicycling = directions.get_from_api(start, end, BICYCLING_MODE)
        data_driving = directions.get_from_api(start, end, DRIVING_MODE)
        data_transit_day = directions.get_from_api(start, end, TRANSIT_MODE, tomorrow_day)
        data_transit_night = directions.get_from_api(start, end, TRANSIT_MODE, tomorrow_night)

        for data in [data_walking, data_bicycling, data_driving]:
            self.assertIsInstance(data, dict)
            self.assertEqual(sorted(data.keys()), ["dist", "time"])
        self.assertEqual(sorted(data_transit_day.keys()), ["main", "steps"])
        self.assertLess(data_driving["time"], data_bicycling["time"])
        self.assertLess(data_bicycling["time"], data_walking["time"])
        self.assertLess(data_driving["time"], data_transit_day["main"]["time"])

        self.assertEqual(len(data_transit_day["steps"]), 3)
        self.assertEqual(data_transit_day["steps"][1]["details"]["line"], '5')
        self.assertEqual(data_transit_night["steps"][1]["details"]["line"], 'N01')

        dist_steps = sum([step["dist"] for step in data_transit_day["steps"]])
        time_steps = sum([step["time"] for step in data_transit_day["steps"]])
        self.assertEqual(dist_steps, data_transit_day["main"]["dist"])
        self.assertLessEqual(time_steps, data_transit_day["main"]["time"])
