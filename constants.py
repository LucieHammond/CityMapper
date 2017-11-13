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

# Couleurs des lignes de métro à Paris
LINE_COLORS = {'1': '#ffcd00', '2': '#003ca6', '3': '#837902', '3B': '#6ec4e8', '4': '#be418d', '5': '#ff7e2e',
               '6': '#6eca97', '7': '#fa9aba', '7B': '#6eca97', '8': '#e19bdf', '9': '#b6bd00', '10': '#c9910d',
               '11': '#704b1c', '12': '#007852', '13': '#6ec4e8', '14': '#62259d', 'RER A': '#d1302f',
               'RER B': '#427dbd', 'RER C': '#fcd946', 'RER D': '#5e9620', 'RER E': '#bd76a1', 'Tram T4': '#f2af00'}