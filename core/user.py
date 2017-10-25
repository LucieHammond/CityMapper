# -*- coding: utf-8 -*-

from constants import FASTEST, SHORTEST, CHEAPEST, LESS_WALKING, SIMPLEST, WEATHER_IMPACT, LESS_PAINFUL, \
    VELIB_NO_SUBSCRIPTION, VELIB_SUBSCRIPTION_30M, VELIB_SUBSCRIPTION_45M, VELIB_TICKETS_30M, \
    AUTOLIB_PRET_A_ROULER, AUTOLIB_PREMIUM, AUTOLIB_FIRST_RENTING_OFFER, \
    SUBWAY_NO_TITLE, SUBWAY_NAVIGO_SUBSCRIPTION, SUBWAY_TICKETS_BOOK, SUBWAY_TICKETS_REDUCED
from dateutil.relativedelta import relativedelta
from datetime import date


class User(object):
    """ Utilisateur qui se connecte au système et initie une recherche d'itinéraire à ses trajets """

    # Nombre total d'utilisateurs enregistrés
    total_users = 0

    def __init__(self, username, password, birthdate):
        if birthdate > date.today():
            raise ValueError("Date de naissance invalide : {}. \n"
                             "Votre date de naissance ne peut pas être supérieure à la date actuelle".format(birthdate))

        User.total_users += 1
        self._id = User.total_users
        self._username = username
        self._password = password
        self._birthdate = birthdate

        # Par défault, l'utilisateur ne dispose d'aucun forfait
        self._subscriptions = {"velib": VELIB_NO_SUBSCRIPTION,
                               "autolib": AUTOLIB_PRET_A_ROULER,  # (abonnement de base gratuit pour Autolib)
                               "subway": SUBWAY_NO_TITLE}
        self._driving_licence = True

        # Importance accordée aux différents critères de choix :
        # 0: aucune, 1: faible, 2: mitigée, 3: sérieuse, 4: forte, 5: maximale
        self._preferences = {FASTEST: 5, SHORTEST: 0, CHEAPEST: 3, LESS_WALKING: 1, SIMPLEST: 2, WEATHER_IMPACT: 4,
                             LESS_PAINFUL: 4}

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def age(self):
        return relativedelta(date.today(),self._birthdate).years

    @property
    def preferences(self):
        return self._preferences

    @preferences.setter
    def preferences(self, value):
        """ :type value: dict( {critère : note de 0 à 5, ...} ) """
        if sorted(value.keys()) != [CHEAPEST, FASTEST, LESS_PAINFUL, LESS_WALKING, SHORTEST, SIMPLEST, WEATHER_IMPACT]:
            raise ValueError
        for val in value.values():
            if val not in range(0,6):
                raise ValueError
        self._preferences = value

    @property
    def driving_licence(self):
        return self._driving_licence

    @driving_licence.setter
    def driving_licence(self, value):
        """ :type value: bool """
        self._driving_licence = value

    @property
    def subscriptions(self):
        return self._subscriptions

    def set_subscriptions_infos(self, velib, autolib, subway):
        if velib not in [VELIB_NO_SUBSCRIPTION, VELIB_SUBSCRIPTION_30M, VELIB_SUBSCRIPTION_45M, VELIB_TICKETS_30M]:
            raise ValueError
        if autolib not in [AUTOLIB_PRET_A_ROULER, AUTOLIB_PREMIUM, AUTOLIB_FIRST_RENTING_OFFER]:
            raise ValueError
        if subway not in [SUBWAY_NO_TITLE, SUBWAY_NAVIGO_SUBSCRIPTION, SUBWAY_TICKETS_BOOK, SUBWAY_TICKETS_REDUCED]:
            raise ValueError
        self._subscriptions = {"velib": velib, "autolib": autolib, "subway": subway}

    def print_user_infos(self, detailed=False):
        print "Utilisateur {} : {} ({} ans)".format(self._id, self._username, self.age)
        if detailed:
            print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - "
            print "Abonnements :"
            print " - Velib :", self._subscriptions["velib"]
            print " - Autolib :", self._subscriptions["autolib"]
            print " - Transports en commun :", self._subscriptions["subway"]
            print "Préférences :"
            for preference, value in self._preferences.items():
                print " - {} : {}".format(preference, str(value))
            print "Permis de conduire : {}\n".format("Oui" if self._driving_licence else "Non")
