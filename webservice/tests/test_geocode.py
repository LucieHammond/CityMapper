# -*- coding: utf-8 -*-

import unittest
from webservice.geocode import Geocode


class GeocodeTest(unittest.TestCase):
    """ Test Case des méthodes du module 'geocode' """

    def test_get_api(self):
        geocode = Geocode()
        right_address = "5 avenue Sully-Prudhomme, Châtenay-Malabry"
        wrong_address = "kuqzydgk<hjksc"
        data = geocode.get_from_api(right_address)
        self.assertIsInstance(data, tuple)
        self.assertEqual(len(data), 2)
        self.assertGreater(data[0], 48.76)
        self.assertLess(data[0], 48.77)
        self.assertGreater(data[1], 2.28)
        self.assertLess(data[1], 2.29)

        error = geocode.get_from_api(wrong_address)
        self.assertIsInstance(error, Exception)
