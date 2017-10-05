
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


class InvalidReplyError(Exception):

    def __init__(self, code):
        self._code = code

    def __str__(self):
        return "API responded with invalid status code {}".format(self._code)
