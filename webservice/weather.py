# -*- coding: utf-8 -*-

import time
from api_manager import ApiManager, ParamNotFoundError

OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast"
API_KEY = "7ca1bf686720bb911d4ebfabaf550fac"
PARIS_ID = 6455259


class Weather(ApiManager):

    def __init__(self):
        default_settings = {"APPID": API_KEY, "id": PARIS_ID}
        ApiManager.__init__(self, OPENWEATHER_API_URL, default_settings)

    def get_from_api(self, timestamp=time.time()):
        """"
        On retourne les données suivantes :
        - température (en Celsius)
        - pluie (en mm sur 3h)
        - neige (en mm sur 3h)
        - vent (en m/s)
        """
        response = self._call_api()

        data = dict()
        try:
            # Take the closest forecast
            record = sorted(response["list"], key=lambda elem: abs(timestamp - elem["dt"]))[0]
            data["temperature"] = round(record["main"]["temp"] - 273.15, 2)  # Conversion Kelvin -> Celsius
            data["rain"] = record["rain"]["3h"] if "rain" in record else 0
            data["wind"] = record["wind"]["speed"] if "wind" in record else 0
            data["snow"] = record["snow"]["3h"] if "snow" in record else 0
        except KeyError as e:
            raise ParamNotFoundError(e.message)
        else:
            return data
