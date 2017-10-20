# -*- coding: utf-8 -*-

import time
from webservice.api_manager import ApiManager, ParamNotFoundError

OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast"
API_KEY = "7ca1bf686720bb911d4ebfabaf550fac"
PARIS_ID = 6455259


class Weather(ApiManager):
    """ Web Service météorologique qui fait appel à l'API Forecast de Open Weather Map """

    def __init__(self):
        default_settings = {"APPID": API_KEY, "id": PARIS_ID}
        ApiManager.__init__(self, OPENWEATHER_API_URL, default_settings)

    def get_from_api(self, timestamp=time.time()):
        """" Renvoie les informations météorologiques observées sur Paris au moment du départ

        :param timestamp: moment de l'observation (par défault maintenant)
        :return:
        - temperature (en Celsius)
        - rain (en mm sur 3h)
        - snow (en mm sur 3h)
        - wind (en m/s)
        :rtype: dict

        """
        response = self._call_api()

        data = dict()
        try:
            # On prend la prévision la plus proche dans le temps
            record = sorted(response["list"], key=lambda elem: abs(timestamp - elem["dt"]))[0]
            data["temperature"] = round(record["main"]["temp"] - 273.15, 2)  # Conversion Kelvin -> Celsius
            data["rain"] = record["rain"]["3h"] if "rain" in record else 0
            data["wind"] = record["wind"]["speed"] if "wind" in record else 0
            data["snow"] = record["snow"]["3h"] if "snow" in record else 0
        except KeyError as e:
            raise ParamNotFoundError(e.message)
        else:
            return data
