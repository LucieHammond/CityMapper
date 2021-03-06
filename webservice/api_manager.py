# -*- coding: utf-8 -*-

import requests


class ApiManager(object):
    """ Gestionnaire de communication avec une API dont on renseigne l'URL et les paramêtres à passer par défaut """

    def __init__(self, url, default_settings=None):
        self._url = url
        self._default_settings = default_settings if default_settings else dict()

    def _call_api(self, payload=None):
        """ Effectue une requête GET vers l'API et retourne la réponse renvoyée

        :param payload: les paramêtres personnalisables de la requête à passer dans l'URL
        :return: la réponse du serveur (au format json) sous forme de dictionnaire

        En cas d'erreur:
        - Affiche un message explicite sur le type de problème rencontré
        - Déclenche l'erreur générique ApiCallError

        """

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
            raise ApiCallError()

        except InvalidReplyError as e:
            print "Incorrect reply : {}".format(e)
            raise ApiCallError()

        except Exception as e:
            print "Error while recovering response from API.\n{}".format(e.message)
            raise ApiCallError()

        else:
            return data

    def get_from_api(self, **kwargs):
        """
            Effectue un appel à l'API pour demander et obtenir des données
            Renvoie les informations utiles dans un format simplifié et pratique
            Cette méthode est implémentée de façon spécifique dans les classes filles

            :param kwargs: paramêtres éventuels pour cibler la demande
        """
        raise NotImplementedError


class InvalidReplyError(Exception):

    def __init__(self, code):
        self._code = code

    def __str__(self):
        return "API responded with invalid status code {}".format(self._code)


class ApiCallError(Exception):
    def __str__(self):
        return "Une erreur s'est produite au moment de récupérer les données.\n" \
               "Vérifiez votre connexion à Internet ou relancez le système"


class ParamNotFoundError(Exception):

    def __init__(self, param):
        self._param = param

    def __str__(self):
        return "Un problème est survenu lors de l'analyse de la réponse renvoyée par l'API\n"" \
        ""Certaines données sont manquantes ou apparaissent dans un format innatendu (comme {})".format(self._param)
