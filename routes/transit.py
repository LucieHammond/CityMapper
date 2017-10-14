# -*- coding: utf-8 -*-

from route import Route

# Forfaits métro possibles
NAVIGO_SUBSCRIPTION = "SUBWAY_NAVIGO_SUBSCRIPTION"  # Or any other unlimited pass
TICKETS_BOOK = "SUBWAY_TICKETS_BOOK"
TICKETS_REDUCED_PRICE = "SUBWAY_TICKETS_REDUCED_PRICE"
NO_RATP_TITLE = "SUBWAY_NO_TITLE"


class SubwayRoute(Route):

    def calculate_route(self):
        pass