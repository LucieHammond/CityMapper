# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from stations import Stations
from api_manager import ParamNotFoundError

TOTAL_STATIONS = 1122 # 1122 stations Velib
SEEKING_DIST = 800 # We search stations at less than 800m


class Velib(Stations):

    dataset= "stations-velib-disponibilites-en-temps-reel"

    def __init__(self):
        refine = {"status": "OPEN", "contract_name" : "Paris"}
        url = self.shape_url(rows=TOTAL_STATIONS, refine=refine)
        Stations.__init__(self, url)

    def find_data(self, point, start):
        """ Renvoie la liste des 5 stations les plus proches du point indiqué """

        latitude = str(point[0])
        longitude = str(point[1])
        now = datetime.utcnow()

        self._url += "&geofilter.distance={}%2C{}%2C{}".format(latitude,longitude,str(SEEKING_DIST))
        self._url += "&sort=dist"

        response = self.call_api()
        best_stations = list()
        infos = ["name", "address", "position", "bonus"]

        try:
            found = 0
            stations = iter(response["records"])
            while found < 5:
                station = next(stations)
                last_update = datetime.strptime(station["fields"]["last_update"], '%Y-%m-%dT%H:%M:%S+00:00')
                if now - last_update > timedelta(minutes=15):
                    continue
                if start and station["fields"]["available_bikes"] > 0:
                    found +=1
                    data = {param: value for param,value in station["fields"].items() if param in infos}
                    data["places"] = station["fields"]["available_bikes"]
                    best_stations.append(data)

                elif not start and station["fields"]["aavailable_bike_stands"] > 0:
                    found += 1
                    data = {param: value for param, value in station["fields"].items() if param in infos}
                    data["places"] = station["fields"]["available_bikes_stands"]
                    best_stations.append(data)

        except KeyError as e:
            raise ParamNotFoundError(e.message)
        finally:
            return best_stations

velib = Velib()
print velib.find_data(point=(48.8496,2.3488), start=True)