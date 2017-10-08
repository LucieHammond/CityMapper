# -*- coding: utf-8 -*-


class Route():

    def __init__(self, ride):
        self._ride = ride
        self._time = None
        self._distance = None
        self._modes_breakdown = None

        self._calculate_route()

    @property
    def time(self):
        return self._time

    @property
    def distance(self):
        return self._distance

    @property
    def modes_breakdown(self):
        return self._modes_breakdown

    def _calculate_route(self):
        raise NotImplementedError

    def _compute_price(self):
        raise NotImplementedError

    def _compute_confort(self):
        raise NotImplementedError

    def _compute_risk(self):
        raise NotImplementedError

    def _compute_environmental_impact(self):
        raise NotImplementedError