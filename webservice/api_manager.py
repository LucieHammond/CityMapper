# -*- coding: utf-8 -*-

import requests


class ApiManager:

    def __init__(self, url):
        self._url = url

    def call_api(self):

        try:
            result = requests.get(self._url)

            if result.status_code != 200:
                raise InvalidReplyError(result.status_code)
            else:
                data = result.json()

        except requests.RequestException as e:
            print "Error while trying to call API.\n{}".format(e.message)

        except InvalidReplyError as e:
            print "Incorrect reply : {}".format(e)

        except Exception as e:
            print "Error while recovering response from API.\n{}".format(e.message)

        else:
            return data

    def find_data(self, params):
        """ Renvoie un dictionnaire contenant les informations voulues (params) renvoyées par l'API"""

        response = self.call_api()
        data = {}
        for param in params:
            if param in response:
                data[param] = response[param]
            else:
                raise ParamNotFoundError(param)
        return data


class InvalidReplyError(Exception):

    def __init__(self, code):
        self._code = code

    def __str__(self):
        return "API responded with invalid status code {}".format(self._code)


class ParamNotFoundError(Exception):

    def __init__(self, param):
        self._param = param

    def __str__(self):
        return "Unable to find param '{}' in API's response".format(self._param)