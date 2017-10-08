# -*- coding: utf-8 -*-

from api_manager import ApiManager
from datetime import datetime, timedelta

OPENDATA_API_URL = "https://opendata.paris.fr/api/records/1.0/search/"
MAX_UPDATE_DELAY = 20  # en minutes


class Stations(ApiManager):
    """
        Gestionnaire d'API lié à la recherche de données sur les infrastructures de transport publiques (stations)
        qui utilise l'une des API de Open Data Paris (Velib, Autolib...)
    """

    def __init__(self, dataset, default_facets, total_rows, infos):
        default_settings = {"dataset": dataset, "rows": total_rows}
        for facet, value in default_facets.items():
            param = "refine." + facet
            default_settings[param] = value
        ApiManager.__init__(self, OPENDATA_API_URL, default_settings)
        self._infos_to_get = infos

    @staticmethod
    def _config_geofilter(point, distance):
        """ Configure les paramêtres à envoyer dans la requête pour filtrer géographiquement les stations """

        latitude = str(point[0])
        longitude = str(point[1])

        # On veut recevoir les stations triées par ordre décroissant de leur distance au point donné
        params = dict({"sort": "dist"})
        # Les stations sont filtrées suivant une distance maximale à ne pas dépasser
        params["geofilter.distance"] = latitude + "," + longitude + "," + str(distance)

        return params

    def _parse_response(self, response, key_param, real_time):
        """ Analyse la réponse renvoyée par l'API pour en extraires les informations importantes

        :param response: réponse de l'API à la requête effectuée
        :param key_param: nom du paramêtre indiquant les places disponibles (sur lequel on sélectionne les stations)
        :param real_time: True si la course cherchée est imminente (sinon pas besoin de vérifier les disponibilités)
        :return: liste des 5 stations (au plus) les mieux adaptées à la demande

        """

        best_stations = list()
        now = datetime.utcnow()

        found = 0
        stations = iter(response["records"])
        while found < 5:
            try:
                station = next(stations)
            except StopIteration:
                return best_stations

            data = dict()
            if real_time:
                if "last_update" in station["fields"] and not check_delay(now, station["fields"]["last_update"]):
                    continue
                if station["fields"][key_param] > 0:
                    data["places"] = station["fields"][key_param]
                else:
                    continue

            data.update({param: value for param, value in station["fields"].items() if param in self._infos_to_get})
            best_stations.append(data)
            found += 1

        return best_stations

    def get_from_api(self, **kargs):
        raise NotImplementedError


# Fonctions utiles
def check_delay(date, last_update_string):
    """ Vérifie que les données de disponiblités ont été mise à jour récemment """
    last_update = datetime.strptime(last_update_string, '%Y-%m-%dT%H:%M:%S+00:00')
    return date - last_update < timedelta(minutes=MAX_UPDATE_DELAY)
