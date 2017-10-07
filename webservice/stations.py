# -*- coding: utf-8 -*-

from api_manager import ApiManager
from datetime import datetime, timedelta

OPENDATA_API_URL = "https://opendata.paris.fr/api/records/1.0/search/"
MAX_UPDATE_DELAY = 20  # en minutes


class Stations(ApiManager):

    def __init__(self, dataset, default_facets, total_rows, infos):
        default_settings = {"dataset": dataset, "rows": total_rows}
        for facet, value in default_facets.items():
            param = "refine." + facet
            default_settings[param] = value
        ApiManager.__init__(self, OPENDATA_API_URL, default_settings)
        self._infos_to_get = infos

    @staticmethod
    def _config_geofilter(point, distance):

        latitude = str(point[0])
        longitude = str(point[1])

        params = {"sort": "dist"}
        params["geofilter.distance"] = latitude + "," + longitude + "," + str(distance)

        return params

    def _parse_response(self, response, key_param, real_time):

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


# Useful functions
def check_delay(date, last_update_string):
    last_update = datetime.strptime(last_update_string, '%Y-%m-%dT%H:%M:%S+00:00')
    return date - last_update < timedelta(minutes=MAX_UPDATE_DELAY)
