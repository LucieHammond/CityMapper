# -*- coding: utf-8 -*-

from stations import Stations
from api_manager import ParamNotFoundError

AUTOLIB_STATIONS = 1014  # 1014 stations Autolib
SEEKING_DIST = 1000  # We search stations at less than 1km


class Autolib(Stations):

    dataset = "autolib-disponibilite-temps-reel"

    def __init__(self):
        facets = {"status": "ok"}
        infos_to_get = ["public_name", "address", "geo_point"]
        Stations.__init__(self, Autolib.dataset, facets, AUTOLIB_STATIONS, infos_to_get)

    def get_from_api(self, point, is_start, real_time=True):
        """ Renvoie la liste des 5 stations les plus proches du point indiqué """

        params = self._config_geofilter(point, SEEKING_DIST)
        response = self._call_api(params)

        try:
            if is_start:
                best_stations = self._parse_response(response, "cars", real_time)
            else:
                best_stations = self._parse_response(response, "slots", real_time)

        except KeyError as e:
            raise ParamNotFoundError(e.message)

        else:
            return best_stations
