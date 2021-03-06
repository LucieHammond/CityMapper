# -*- coding: utf-8 -*-

from stations import Stations
from api_manager import ParamNotFoundError

AUTOLIB_STATIONS = 1014  # 1014 stations Autolib
SEEKING_DIST = 1300  # On cherche des stations à moins d'1.3km


class Autolib(Stations):
    """ Web Service de vérification des disponibilités en temps réel des Autolibs en Ile de France """

    dataset = "autolib-disponibilite-temps-reel"

    def __init__(self):
        facets = {"status": "ok"}
        infos_to_get = ["public_name", "address", "geo_point"]
        Stations.__init__(self, Autolib.dataset, facets, AUTOLIB_STATIONS, infos_to_get)

    def get_from_api(self, point, is_start, real_time=True):
        """ Renvoie la liste des 3 stations Autolib les plus proches du point indiqué

        :param point: point géographique autour duquel on filtre les stations (latitude, longitude)
        :param is_start:
        - True si on cherche des stations de départ (avec des voitures)
        - False si on cherche des stations d'arrivée (avec des emplacements libres)
        :param real_time: True si la course cherchée est imminente
        :return: [{nom de la station, adresse, position, nb de places} pour chaque station]

        """

        params = self._config_geofilter(point, SEEKING_DIST)

        try:
            response = self._call_api(params)
            if is_start:
                best_stations = self._parse_response(response, "cars", real_time)
            else:
                best_stations = self._parse_response(response, "slots", real_time)

        except KeyError as e:
            return ParamNotFoundError(e.message)

        except Exception as error:
            return error

        else:
            return best_stations
