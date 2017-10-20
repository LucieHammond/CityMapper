# -*- coding: utf-8 -*-

import time
from routes.route import Route
from webservice.directions import Directions, WALKING_MODE, DRIVING_MODE, TRANSIT_MODE

# Forfaits métro possibles
NAVIGO_SUBSCRIPTION = "SUBWAY_NAVIGO_SUBSCRIPTION"  # Or any other unlimited pass
TICKETS_BOOK = "SUBWAY_TICKETS_BOOK"
TICKETS_REDUCED_PRICE = "SUBWAY_TICKETS_REDUCED_PRICE"
NO_RATP_TITLE = "SUBWAY_NO_TITLE"


class SubwayRoute(Route):

    def __init__(self, ride):
        self._start_station = None
        self._end_station = None
        self._steps = None
        Route.__init__(self, ride)

    def _calculate_route(self):
        transit = Directions()
        ride = self._ride
        response = transit.get_from_api(ride.start, ride.end, "transit")
        self._time = response["main"]["time"]
        self._distance = response["main"]["dist"]

        self._modes_breakdown = {WALKING_MODE: response["steps"][0]["time"] + response["steps"][2]["time"],
                                 TRANSIT_MODE: response["steps"][1]["time"]}



'''from core.ride import Ride

start = (48.836239, 2.242632)
end = (48.839659, 2.290922)

ride = Ride(start, end, time.time() + 25000)
transit = SubwayRoute(ride)
print(transit._calculate_route())'''




