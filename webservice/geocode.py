# -*- coding: utf-8 -*-

from webservice.api_manager import ApiManager, ParamNotFoundError

GEOCODE_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
API_KEY = "AIzaSyA7MMbN_GUUewFBuSpkuS-ALCNnjA7mc8E"
ZERO_RESULTS = "ZERO_RESULTS"


class Geocode(ApiManager):
    """ Web Service de conversion d'une adresse écrite (chaine de caractère) en coordonnées géographies
        Ce service qui fait appel à l'API Géocode de Google Maps """

    def __init__(self):
        default_settings = {"key": API_KEY}
        ApiManager.__init__(self, GEOCODE_API_URL, default_settings)

    def get_from_api(self, address):
        params=dict()
        params["address"] = address

        try:
            response = self._call_api(params)
            if response["status"] == ZERO_RESULTS:
                raise ZeroResultsError(address)
            data = self._parse_response(response)

        except KeyError as e:
            return ParamNotFoundError(e.message)

        except Exception as error:
            return error

        else:
            return data

    @staticmethod
    def _parse_response(response):

        geometry = response["results"][0]["geometry"]
        latitude = geometry["location"]["lat"]
        longitude = geometry["location"]["lng"]
        return (latitude, longitude)


class ZeroResultsError(Exception):

    def __init__(self, address):
        self._address = address

    def __str__(self):
        return "Impossible de trouver les coordonnées géographiques correspondant à l'adresse: {}".format(self._address)
