# -*- coding: utf-8 -*-

""" Module répertoriant toutes les constantes partagées """

# Critères de préférences pour un trajet
FASTEST = "FAST"  # Le plus rapide (temps total)
SHORTEST = "SHORT"  # Le plus court (distance totale)
CHEAPEST = "CHEAP"  # Le moins cher (prix)
LESS_WALKING = "LESS_WALKING"  # Le moins de marche à pied (temps de marche)
SIMPLEST = "SIMPLE"  # Le plus simple (moins de changements et correspondances)
WEATHER_IMPACT = "WEATHER_IMPACT"  # Le plus adapté à la météo (pluie, neige, vent, température)
LESS_PAINFUL = "LESS_PAINFUL"  # Le plus comfortable par rapport aux bagages transportés

# Types de bagages
SUITCASE = "SUITCASE"
BACKPACK = "BACKPACK"
HANDBAG = "HANDBAG"
BULKY = "BULKY"

# Les modes de déplacement possibles
DRIVING_MODE = "driving"
BICYCLING_MODE = "bicycling"
WALKING_MODE = "walking"
TRANSIT_MODE = "transit"

# Forfaits Velib possibles
VELIB_SUBSCRIPTION_30M = "VELIB_SUBSCRIPTION_30M"
VELIB_SUBSCRIPTION_45M = "VELIB_SUBSCRIPTION_45M"
VELIB_TICKETS_30M = "VELIB_TICKETS_30M"
VELIB_NO_SUBSCRIPTION = "VELIB_NO_SUBSCRIPTION"

# Forfaits Autolib possibles
AUTOLIB_PREMIUM = "AUTOLIB_PREMIUM"
AUTOLIB_PRET_A_ROULER = "AUTOLIB_PRET_A_ROULER"
AUTOLIB_FIRST_RENTING_OFFER = "AUTOLIB_FIRST_RENTING_OFFER"

# Forfaits métro possibles
SUBWAY_NAVIGO_SUBSCRIPTION = "SUBWAY_NAVIGO_SUBSCRIPTION"  # Or any other unlimited pass
SUBWAY_TICKETS_BOOK = "SUBWAY_TICKETS_BOOK"
SUBWAY_TICKETS_REDUCED = "SUBWAY_TICKETS_REDUCED"
SUBWAY_NO_TITLE = "SUBWAY_NO_TITLE"