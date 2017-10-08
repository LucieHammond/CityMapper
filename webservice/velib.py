# -*- coding: utf-8 -*-

from stations import Stations
from api_manager import ParamNotFoundError

VELIB_STATIONS = 1122  # 1122 stations Velib
SEEKING_DIST = 800  # On cherche des stations à moins de 800m


class Velib(Stations):
    """ Web Service de vérification des disponibilités en temps réel des Vélibs sur Paris """

    dataset = "stations-velib-disponibilites-en-temps-reel"

    def __init__(self):
        facets = {"status": "OPEN", "contract_name": "Paris"}
        infos_to_get = ["name", "address", "position", "bonus"]
        Stations.__init__(self, Velib.dataset, facets, VELIB_STATIONS, infos_to_get)

    def get_from_api(self, point, is_start, real_time=True):
        """ Renvoie la liste des 3 stations Velib les plus proches du point indiqué

        :param point: point géographique autour duquel on filtre les stations (latitude, longitude)
        :param is_start:
        - True si on cherche des stations de départ (avec des vélos)
        - False si on cherche des stations d'arrivée (avec des emplacements libres)
        :param real_time: True si la course cherchée est imminente
        :return: [{nom de la station, adresse, position, bonus, nb de places} pour chaque station]

        """

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
