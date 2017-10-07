# -*- coding: utf-8 -*-

import requests


class ApiManager:

    def __init__(self, url, default_settings=None):
        self._url = url
        self._default_settings = default_settings if default_settings else dict()

    def _call_api(self, payload=None):

        if not payload:
            payload = {}
        payload.update(self._default_settings)

        try:
            result = requests.get(self._url, params=payload)

            if result.status_code != 200:
                raise InvalidReplyError(result.status_code)
            else:
                data = result.json()

        except requests.RequestException as e:
            print "Error while trying to call API.\n{}".format(e.message)
            raise ApiCallError

        except InvalidReplyError as e:
            print "Incorrect reply : {}".format(e)
            raise ApiCallError

        except Exception as e:
            print "Error while recovering response from API.\n{}".format(e.message)
            raise ApiCallError

        else:
            return data

    def get_from_api(self, **kargs):
        """ Renvoie un dictionnaire contenant les informations voulues renvoyées par l'API"""
        raise NotImplementedError


class InvalidReplyError(Exception):

    def __init__(self, code):
        self._code = code

    def __str__(self):
        return "API responded with invalid status code {}".format(self._code)


class ApiCallError(Exception):
    pass


class ParamNotFoundError(Exception):

    def __init__(self, param):
        self._param = param

    def __str__(self):
        return "Unable to find param '{}' in API's response".format(self._param)