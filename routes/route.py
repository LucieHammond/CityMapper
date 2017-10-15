# -*- coding: utf-8 -*-

# Les modes de déplacement possibles
DRIVING_MODE = "driving"
BICYCLING_MODE = "bicycling"
WALKING_MODE = "walking"
TRANSIT_MODE = "transit"


class Route():

    def __init__(self, ride):
        self._ride = ride
        self._time = None
        self._distance = None
        self._modes_breakdown = None
        self._steps = None

        self.calculate_route()

    @property
    def time(self):
        return self._time

    @property
    def distance(self):
        return self._distance

    @property
    def modes_breakdown(self):
        return self._modes_breakdown

    def calculate_route(self):
        raise NotImplementedError

    def get_price(self):
        raise NotImplementedError

    def get_discomfort(self):
        raise NotImplementedError

    def get_transfers_number(self):
        return len(self._steps) - 1

    def get_walking_time(self):
        return self._modes_breakdown[WALKING_MODE]
