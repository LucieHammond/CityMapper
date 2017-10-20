# -*- coding: utf-8 -*-

import time
from routes.bicycling import VelibRoute
from routes.driving import AutolibRoute
from routes.transit import SubwayRoute
from webservice.weather import Weather


class Ride():

    def __init__(self, start, end, departure_time, charge=None, velib=None, autolib=None, transit = None, minimum_walking=None):
        self.start = start
        self.end = end
        self.departure_time = departure_time
        weather = Weather()
        self._meteo = weather.get_from_api()
        self._charge = charge
        self._velib = velib
        self._autolib = autolib
        self._transit = transit
        self._minimum_walking = minimum_walking


    def compare(self, ride):
        autolib_route = AutolibRoute(ride)
        velib_route = VelibRoute(ride)
        transit_route = SubwayRoute(ride)
        liste_objet = [autolib_route, velib_route, transit_route]
        liste_objet_triees = sorted(liste_objet, key=lambda route: route.time)
        if self._meteo["rain"] > 10 or self._meteo["snow"] > 5 or self._charge:
            i = liste_objet_triees.index(velib_route)
            liste_objet_triees[i], liste_objet_triees[-1] = liste_objet_triees[-1], liste_objet_triees[i]
        if self._autolib:
            i = liste_objet_triees.index(autolib_route)
            liste_objet_triees[i], liste_objet_triees[0] = liste_objet_triees[0], liste_objet_triees[i]
        if self._velib:
            i = liste_objet_triees.index(velib_route)
            liste_objet_triees[i], liste_objet_triees[0] = liste_objet_triees[0], liste_objet_triees[i]
        if self._transit:
            i = liste_objet_triees.index(transit_route)
            liste_objet_triees[i], liste_objet_triees[0] = liste_objet_triees[0], liste_objet_triees[i]
        if self._minimum_walking:
            liste_objet_triees = sorted(liste_objet, key=lambda route: route.modes_breakdown["walking"])
        return liste_objet_triees




start = (48.836239, 2.242632)
end = (48.839659, 2.290922)

ride = Ride(start, end, time.time() + 25000, minimum_walking=True)

resultat = ride.compare(ride)
print(resultat)
