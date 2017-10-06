# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from api_manager import ApiManager, ParamNotFoundError

INFOCLIMAT_API_URL = "http://www.infoclimat.fr/public-api/gfs/json"
API_KEY = "BhxTRA5wXX9XeldgVSNQeQJqUGUPeVN0AHxSMQpvBXgEbwRlVDRdO14wAXwHKAo8WXQFZg80BjZTOAR8DnxePwZsUz8OZV06VzhXMlV6UHsCLFAxDy9TdABqUjcKeQVnBG8EZFQpXTZeNwF9BzYKOFlqBXoPLwY%2FUzUEYw5kXj8GZ1M0DmxdPlc4VypVelBhAjhQZA82U20AZVIxCmEFZARmBDZUN11qXjQBfQc2CjhZawVnDzMGOFM1BGUOfF4iBhxTRA5wXX9XeldgVSNQeQJkUG4PZA%3D%3D"
CODE = "f0f4e9612e42743fd941e20c77fa8c4a"

LATITUDE_PARIS = 48.85341
LONGITUDE_PARIS = 2.3488


class Weather(ApiManager):

    def __init__(self):
        url = "{0}?_ll={1},{2}&_auth={3}&_c={4}".format(
            INFOCLIMAT_API_URL,
            str(LATITUDE_PARIS),
            str(LONGITUDE_PARIS),
            API_KEY,
            CODE)

        ApiManager.__init__(self, url)

    def find_data(self, day=datetime.now()):
        """"
        On retourne les données suivantes :
        - température (en Celsius)
        - pluie (en mm sur 3h)
        - vent (en km/h)
        - risque de neige (oui ou non)
        """
        response = self.call_api()

        date = closest_available_hour(day)
        data = dict()

        try:
            record = response[date]
            data["temperature"] = record["temperature"]["sol"] - 273.15  # Conversion Kelvin -> Celsius
            data["rain"] = record["pluie"]
            data["wind"] = record["vent_moyen"]["10m"]
            data["snow"] = (record["risque_neige"] == 'oui')
        except KeyError as e:
            raise ParamNotFoundError(e.message)

        return data


# Fonctions utiles
def closest_available_hour(day):
    """" Les heures disponibles chaque jour pour la météo sont 2h, 5h, 8h, 11h, 14h, 17h, 20h et 23h """

    # Prendre l'horaire displonible le plus proche
    hour = day.hour + day.minute / 60.0 + day.second / 3600.0
    is_next = (hour + 1) % 3 > 1.5

    new_date = day - timedelta(hours=int((hour + 1) % 3), minutes=day.minute, seconds=day.second) + is_next * timedelta(hours=3)

    string_date = new_date.strftime("%Y-%m-%d %H:%M:%S")

    return string_date
