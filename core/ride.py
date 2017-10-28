# -*- coding: utf-8 -*-

from webservice.weather import Weather
from routes.bicycling import VelibRoute
from routes.driving import AutolibRoute
from routes.transit import SubwayRoute
from core.tasks import TasksManager
from constants import FASTEST, SHORTEST, CHEAPEST, LESS_WALKING, SIMPLEST, WEATHER_IMPACT, LESS_PAINFUL, \
    SUITCASE, BULKY, BACKPACK, HANDBAG
from operator import itemgetter
import time

associated_params = {FASTEST: "time", SHORTEST: "distance", CHEAPEST: "price", LESS_WALKING: "walking_time",
                     SIMPLEST: "transfers_nb", WEATHER_IMPACT: "weather_impact", LESS_PAINFUL: "difficulty"}


class Ride(object):
    """ Trajet demandé par l'utilisateur, pour lequel on va calculer plusieurs itinéraires possibles """

    def __init__(self, user, start, end, departure_time):
        if departure_time < time.time():
            raise ValueError("Date de départ invalide : {}. \n"
                             "Le moment du départ ne peut pas antérieur à la date actuelle".format(departure_time))

        self._user = user
        self._start = start
        self._end = end
        self._departure_time = departure_time  # format = timestamp

        self._travellers = 1  # Nombre de voyageurs
        self._luggage = dict()

        # Les préférences pour le trajet sont celles définies dans le profil de l'utilisateur
        self._preferences = user.preferences
        self._weather = self._get_weather()

    @property
    def user(self):
        return self._user

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def departure_time(self):
        return self._departure_time

    @property
    def weather(self):
        return self._weather

    @property
    def travellers(self):
        return self._travellers

    @travellers.setter
    def travellers(self, value):
        """ :type value: int """
        self._travellers = value

    @property
    def luggage(self):
        return self._luggage

    @luggage.setter
    def luggage(self, value):
        """ :type value: dict( {type_bagage : nombre, ...} ) """
        for bag in value.keys():
            if bag not in [SUITCASE, BULKY, BACKPACK, HANDBAG]:
                raise ValueError
        for val in value.values():
            if not isinstance(val, int) or val < 0:
                raise ValueError
        self._luggage = value

    @property
    def preferences(self):
        return self._preferences

    def _get_weather(self):
        """ Appelle l'API de Open Weather Map pour connaître la météo au moment du départ

        :return: {'temperature' (en Celsius), 'rain' (en mm sur 3h), 'snow' (en mm sur 3h), 'wind' (en m/s)}
        """
        weather_service = Weather()
        tm = TasksManager()
        tm.new_task(target=weather_service.get_from_api, args=(self._departure_time, ))
        weather = tm.next_result()
        return weather

    def start_simulation(self):
        """ Calcule les itinéraires possibles en Vélib, Autolib et Transports en commun
        Si plusieurs modes sont possibles, on lance une comparaison des itinéraires pour les classer

        :return:
        - La liste ordonnée des itinéraires possibles (compte tenu des préférences de l'utilisateur)
        - La liste des itinéraires impossibles (objet indiquant le mode de transport et le message à afficher)

        """
        possible_routes = list()
        unsuitable_routes = list()

        # Essayer un itinéraire en Vélib
        unsuitable_msg = self._is_velib_unsuitable()
        if not unsuitable_msg:
            velib_route = VelibRoute(self)
            if velib_route.calculate_route():
                possible_routes.append(velib_route)
            else:
                unsuitable_msg = "Aucun itinéraire en Vélib n'a pu être trouvé"
        if unsuitable_msg:
            unsuitable_routes.append({"mode": "velib", "msg": unsuitable_msg})


        # Essayer un itinéraire en transport en commun
        unsuitable_msg = self._is_transit_unsuitable()
        if not unsuitable_msg:
            subway_route = SubwayRoute(self)
            if subway_route.calculate_route():
                possible_routes.append(subway_route)
            else:
                unsuitable_msg = "Aucun itinéraire n'a pu être trouvé avec les transports en commun"
        if unsuitable_msg:
            unsuitable_routes.append({"mode": "transit", "msg": unsuitable_msg})

        # Essayer un itinéraire en Autolib
        unsuitable_msg = self._is_autolib_unsuitable()
        if not unsuitable_msg:
            autolib_route = AutolibRoute(self)
            if autolib_route.calculate_route():
                possible_routes.append(autolib_route)
            else:
                unsuitable_msg = "Aucun itinéraire en Autolib n'a pu être trouvé"
        if unsuitable_msg:
            unsuitable_routes.append({"mode": "autolib", "msg": unsuitable_msg})

        if len(possible_routes) <= 1:
            return possible_routes, unsuitable_routes

        scores = self._compute_scores(possible_routes)
        ordered_routes = self._compare_routes(scores)
        return ordered_routes, unsuitable_routes

    def _is_velib_unsuitable(self):
        """ Teste si l'utilisateur n'est pas trop jeune ou avec des bagages trop gros/nombreux pour prendre le Velib """
        nb_luggage = 0
        for item in self._luggage.keys():
            if item in [SUITCASE, BULKY]:
                return "Vos bagages sont trop gros et encombrants pour vous permettre de prendre le vélib"
            nb_luggage += 1
        if nb_luggage > 4:
            return "Vous avez trop de bagages à porter pour pouvoir vous déplacer en vélib"
        if self._user.age < 14:
            return "Vous devez être âgé d'au moins 14 ans pour utiliser un Vélib sans accompagnateur"
        return None

    def _is_autolib_unsuitable(self):
        """ Teste si l'utilisateur est en droit de conduire une Autolib """
        if self._user.age < 18:
            return "Vous devez être âgé d'au moins 18 ans pour pouvoir conduire une Autolib"
        if not self._user.driving_licence:
            return "Vous devez avoir obtenu le permis de conduire pour pouvoir utiliser une Autolib"
        return None

    def _is_transit_unsuitable(self):
        """ Teste si l'utilisateur n'a pas de bagages trop encombrants pour prendre les transports en commun """
        nb_luggage = 0
        for item in self._luggage.keys():
            if item == BULKY:
                return "Vos bagages sont trop encombrants pour vous permettre de voyager dans les transports en commun"
            nb_luggage += 1
        if nb_luggage > 5:
            return "Vous avez trop de bagages à porter pour vous déplacer aisément en transports en commun"
        if self._user.age < 6:
            return "En dessous de 6 ans, vous semblez trop jeune pour prendre seul les transports en commun"
        return None

    @staticmethod
    def _compute_scores(possible_routes):
        """ Calcule pour chaque itinéraire et pour chaque critère un score (float) entre 0 (meilleur) et 1 (moins bon)

        :param possible_routes: liste des itinéraires possibles (de type Route)
        :return: dictionnaire des scores {route1: {critère1: score1, critère2: score2 ...}, ... }

        """

        # Les scores sont ramenés sur une échelle comparable
        def normalize_score(score, ref_mini, ref_maxi):
            return (float(score) - float(ref_mini)) / (float(ref_maxi) - float(ref_mini))

        def get_property(route, property):
            dict = {"time": route.time,
                    "distance": route.distance,
                    "price": route.price,
                    "difficulty": route.difficulty,
                    "walking_time": route.walking_time,
                    "weather_impact": route.weather_impact,
                    "transfers_nb": route.transfers_nb}
            return dict[property]

        scores = dict.fromkeys(possible_routes)
        for route in scores.keys():
            scores[route] = {}

        ref_min = dict({"price": 0, "transfers_nb": 2, "difficulty": 0, "weather_impact": 0})
        ref_max = dict({"price": 5, "transfers_nb": 4, "difficulty": 100, "weather_impact": 100})
        ref_min["time"] = min([route.time for route in possible_routes])
        ref_min["distance"] = min([route.distance for route in possible_routes])
        ref_min["walking_time"] = min([route.walking_time for route in possible_routes])
        ref_max["time"] = 1.4 * ref_min["time"]
        ref_max["distance"] = 1.4 * ref_min["distance"]
        ref_max["walking_time"] = 1.4 * ref_min["walking_time"]

        for param in associated_params.values():
            for route in possible_routes:
                scores[route][param] = normalize_score(get_property(route, param), ref_min[param], ref_max[param])

        return scores

    def _compare_routes(self, scores):
        """ Compare les différents itinéraires en pondérant chacun de leurs scores par le coefficient de préférence
            associé au critère sur lequel porte le score

        :param scores: Un dictionnaire qui associe à chaque itinéraire des scores pour tous les critères
        :return: la liste ordonnée des itinéraires possibles compte tenu des préférences de l'utilisateur

        """

        preferences = self._user.preferences
        for route, score in scores.items():
            grade = sum([preferences[criteria] * score[param] for criteria, param in associated_params.items()])
            scores[route]["grade"] = grade

        sorted_scores = sorted(scores.items(), key=lambda x: x[1]["grade"])

        return [score[0] for score in sorted_scores]
