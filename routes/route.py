# -*- coding: utf-8 -*-

from constants import WALKING_MODE


class Route(object):

    def __init__(self, ride):
        self._ride = ride
        self._modes_breakdown = None
        self._steps = None

        self._time = None
        self._distance = None
        self._price = None
        self._transfers_nb = None
        self._discomfort = None
        self._walking_time = None

    @property
    def steps(self):
        return self._steps

    @property
    def time(self):
        if not self._time:
            self._time = 0
            for step in self._steps:
                self._time += step["time"]
        return self._time

    @property
    def distance(self):
        if not self._distance:
            self._distance = 0
            for step in self._steps:
                self._distance += step["dist"]
        return self._distance

    @property
    def price(self):
        if not self._price:
            self._price = self._compute_price()
        return self._price

    @property
    def transfers_nb(self):
        if not self._transfers_nb:
            self._transfers_nb = len(self._steps) - 1
        return self._transfers_nb

    @property
    def discomfort(self):
        if not self._discomfort:
            self._discomfort = self._compute_discomfort()
        return self._discomfort

    @property
    def walking_time(self):
        if not self._walking_time:
            self._walking_time = self._modes_breakdown[WALKING_MODE]
        return self._walking_time

    def calculate_route(self):
        raise NotImplementedError

    def _compute_price(self):
        raise NotImplementedError

    def _compute_discomfort(self):
        raise NotImplementedError

    def display_route(self):
        import datetime
        print "Trajet de {} vers {} en partant le {}".format(
            self._ride.start,
            self._ride.end,
            datetime.datetime.fromtimestamp(self._ride.departure_time).strftime('%Y-%m-%d à %H:%M:%S'))
        print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - "
        print "Recapitulatif :"
        print " - Temps :", self._time
        print " - Distance :", self._distance
        print " - Prix :", self._price
        print " - Nombre de transferts :", self._transfers_nb
        print " - Temps de marche :", self._walking_time
        print " - Agréabilité du trajet (1) :", self._discomfort
        print "(1) Le confort est calculé sur une échelle de 0 (plus agréable) à 2000 (moins agréable)\n"
