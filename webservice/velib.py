# -*- coding: utf-8 -*-

from stations import Stations
from api_manager import ParamNotFoundError

VELIB_STATIONS = 1122  # 1122 stations Velib
SEEKING_DIST = 800  # We search stations at less than 800m


class Velib(Stations):

    dataset = "stations-velib-disponibilites-en-temps-reel"

    def __init__(self):
        facets = {"status": "OPEN", "contract_name": "Paris"}
        infos_to_get = ["name", "address", "position", "bonus"]
        Stations.__init__(self, Velib.dataset, facets, VELIB_STATIONS, infos_to_get)

    def get_from_api(self, point, is_start, real_time=True):
        """ Renvoie la liste des 5 stations les plus proches du point indiqué """

        params = self._config_geofilter(point, SEEKING_DIST)
        response = self._call_api(params)

        try:
            if is_start:
                best_stations = self._parse_response(response, "available_bikes", real_time)
            else:
                best_stations = self._parse_response(response, "available_bike_stands", real_time)

        except KeyError as e:
            raise ParamNotFoundError(e.message)

        else:
            return best_stations
