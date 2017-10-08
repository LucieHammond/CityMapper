# -*- coding: utf-8 -*-

import time
from api_manager import ApiManager, ParamNotFoundError

GMAP_API_URL = "https://maps.googleapis.com/maps/api/directions/json"
API_KEY = "AIzaSyCd5Hw6lEZ0Nq2P4tXQ9ueKq2yIGa_KLrg"

# Les modes de déplacements possibles pour l'API de Google Maps
DRIVING_MODE = "driving"
BICYCLING_MODE = "bicycling"
WALKING_MODE = "walking"
TRANSIT_MODE = "transit"


class Directions(ApiManager):
    """ Web service d'optimisation d'itinéraires qui fait appel à l'API Directions de Google Maps"""

    def __init__(self):
        default_settings = {"key": API_KEY}
        ApiManager.__init__(self, GMAP_API_URL, default_settings)

    def get_from_api(self, origin, destination, mode, departure_time=time.time()):
        """" Renvoie le détail du plus court trajet trouvé grâce

        :param origin: position du départ (latitude, longitude)
        :param destination: position de l'arrivée (latitude, longitude)
        :param mode: mode de déplacement
        :param departure_time: moment du départ (utilisable uniquement pour des trajets en métro)

        """
        params = dict()
        params["origin"] = str(origin[0]) + "," + str(origin[1])
        params["destination"] = str(destination[0]) + "," + str(destination[1])
        params["mode"] = mode
        if mode == TRANSIT_MODE:
            params["transit_mode"] = "subway"
            params["departure_time"] = int(departure_time)

        response = self._call_api(params)
        transit_ride = (mode == TRANSIT_MODE)

        try:
            data = self._parse_response(response, transit_ride)
        except KeyError as e:
            raise ParamNotFoundError(e.message)
        else:
            return data

    @staticmethod
    def _parse_response(response, transit_ride):
        """ Analyse la réponse obtenue et renvoie les informations importantes sous forme simplifiée

        Dans le cas d'un trajet simple (mode de déplacement connu et unique):
        :return: {distance en m, temps en s, adresse de départ, adresse d'arrivée}

        Dans le cas d'un trajet avec transit (transit_ride = True):
        :return:
        { main : {distance en m, temps en s, adresse de départ, adresse d'arrivée}
        steps : [{mode, distance, temps, détails (si portion de parcours en métro)} pour chaque étape]

        """
        route = response["routes"][0]["legs"][0]

        main = dict()
        main["dist"] = route["distance"]["value"]
        main["time"] = route["duration"]["value"]
        main["start_address"] = route["start_address"]
        main["end_address"] = route["end_address"]

        if not transit_ride:
            return main

        data = dict({"main": main})
        steps = list()

        for step in route["steps"]:
            next_step = dict({"mode": step["travel_mode"]})
            next_step["dist"] = step["distance"]["value"]
            next_step["time"] = step["duration"]["value"]

            if step["travel_mode"] == TRANSIT_MODE.upper():
                transit_details = step["transit_details"]

                details = dict()
                details["line"] = transit_details["line"]["short_name"]
                details["direction"] = transit_details["headsign"]
                details["stops"] = transit_details["num_stops"]
                details["start"] = {"name": transit_details["departure_stop"]["name"],
                                    "position": (transit_details["departure_stop"]["location"]["lat"],
                                                 transit_details["departure_stop"]["location"]["lng"])}
                details["end"] = {"name": transit_details["arrival_stop"]["name"],
                                  "position": (transit_details["arrival_stop"]["location"]["lat"],
                                               transit_details["arrival_stop"]["location"]["lng"])}

                next_step["details"] = details

            steps.append(next_step)

        data["steps"] = steps
        return data
