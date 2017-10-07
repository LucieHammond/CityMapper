# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from api_manager import ApiManager, ParamNotFoundError

GMAP_API_URL = "https://maps.googleapis.com/maps/api/directions/json?origin=Paris&destination=Antony&mode=driving&key=<votre_clé>"


class Directions(ApiManager):

    def find_data(self, start, end, mode):
        """ retourner durée totale, décomposition par mode
        mode = walk only, drive only, bicycle only, transit
        """
