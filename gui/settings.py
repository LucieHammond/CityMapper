# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
import time
from constants import BACKPACK, HANDBAG, SUITCASE, BULKY, WALKING_MODE, DRIVING_MODE, BICYCLING_MODE, TRANSIT_MODE, \
    LINE_COLORS


class RideSettingsPage(Frame):
    """ Page principale de définition d'un nouveau trajet """

    def __init__(self, window, system):
        Frame.__init__(self, window, width=1000, height=600, bg="LightSkyBlue1")
        self.pack()
        self.pack_propagate(0)
        self._window = window
        self._system = system

        self._start = StringVar()
        self._end = StringVar()
        self._departure_days = IntVar()
        self._departure_hours = IntVar()
        self._departure_minutes = IntVar()
        self._travellers = IntVar()
        self._backpack = IntVar()
        self._handbag = IntVar()
        self._suitcase = IntVar()
        self._bulky = IntVar()
        self.init_parameters()

        self._map = None
        self._image = None
        self.config_menu()
        self.display_map()
        self._frame = self.settings_form()
        self._frame.pack(fill=BOTH, expand=YES, side=RIGHT, padx=(0, 20), pady=20)
        self._frame.pack_propagate(0)

    def init_parameters(self):
        """ Initialise les paramètres si un trajet est déjà sauvegardé """
        if self._system.current_ride:
            ride = self._system.current_ride
            self._start.set('@ %f,%f' % (ride.start[0], ride.start[1]))
            self._end.set('@ %f,%f' % (ride.end[0], ride.end[1]))
            time_diff = int(ride.departure_time - time.time())
            if time_diff <= 0:
                self._departure_days.set(0)
                self._departure_hours.set(0)
                self._departure_minutes.set(0)
            else:
                self._departure_days.set(time_diff // 86400)
                self._departure_hours.set((time_diff % 86400) // 3600)
                self._departure_minutes.set(int(round((time_diff % 3600) / 60.0)))

            self._travellers.set(ride.travellers)
            self._backpack.set(0)
            self._handbag.set(0)
            self._suitcase.set(0)
            self._bulky.set(0)
            if BACKPACK in ride.luggage:
                self._backpack.set(ride.luggage[BACKPACK])
            if HANDBAG in ride.luggage:
                self._handbag.set(ride.luggage[HANDBAG])
            if SUITCASE in ride.luggage:
                self._suitcase.set(ride.luggage[SUITCASE])
            if BULKY in ride.luggage:
                self._bulky.set(ride.luggage[BULKY])

    def config_menu(self):
        """ Création d'un menu de navigation en haut de la page """

        # Le menubar de tkinter ne fonctionne pas sur Mac OS X. Je simule donc un menu à la main
        menubar = Frame(self, height=30, bg="SlateGray3", relief=RAISED, borderwidth=2)
        menubar.pack(fill=BOTH)
        Label(menubar, text="%s :" % self._system.current_user.username, font=("Lucida", 14, "bold"), bg="SlateGray3")\
            .pack(side=LEFT, padx=(10, 5))
        Button(menubar, text="Mon profil", highlightbackground="SlateGray3", command=self.display_profile_1)\
            .pack(side=LEFT, padx=5)
        Button(menubar, text="Mes préférences", highlightbackground="SlateGray3", command=self.display_profile_2)\
            .pack(side=LEFT, padx=5)
        Button(menubar, text="Deconnexion", highlightbackground="SlateGray3", command=self.deconnection)\
            .pack(side=RIGHT, padx=5)
        self._window.config(menu=menubar)

    def display_map(self):
        """ Ajoute une carte de Paris à gauche """
        self._map = Canvas(self, width=600, height=500, highlightthickness=0)
        self._image = PhotoImage(file="resources/map.gif")
        self._map.create_image(0, 0, anchor=NW, image=self._image)
        self._map.pack(side=LEFT, padx=20, pady=35)

    def display_profile_1(self):
        """ Affiche la page 1 du profil utilisateur (informations) """
        from profile import ProfilePage
        self.pack_forget()
        ProfilePage(self._window, self._system, 1)

    def display_profile_2(self):
        """ Affiche la page 2 du profil utilisateur (préférences) """
        from profile import ProfilePage
        self.pack_forget()
        ProfilePage(self._window, self._system, 2)

    def deconnection(self):
        """ Déconnexion de l'utilisateur et retour à la page d'accueil avec le logos """
        from home import HomePage
        result = self._system.sign_out()
        if not result["success"]:
            showerror('Erreur système', result["error"])
            return
        self.pack_forget()
        HomePage(self._window, self._system)

    def settings_form(self):
        """ Crée et renvoie le formulaire de définition d'un nouveau trajet (qui sera placé à droite) """
        form = Frame(self, bg="LightSkyBlue1")

        Label(form, text="-- Nouveau trajet --", font=("Helvetica", 18, "bold"), bg="LightSkyBlue1").pack(pady=(5, 10))
        italic = ("Lucida", 13, "italic")
        bold = ("Lucida", 14, "bold")

        Label(form, text="Départ :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        Entry(form, textvariable=self._start, width=40).pack(padx=5, pady=(0, 10))

        Label(form, text="Arrivée :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        Entry(form, textvariable=self._end, width=40).pack(padx=5, pady=(0, 10))

        Label(form, text="Moment du départ :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        departure_frame = Frame(form, bg="LightSkyBlue1")
        departure_frame.pack(padx=5, pady=(0, 10))
        Label(departure_frame, text="Dans", bg="LightSkyBlue1").grid(row=1, column=1, padx=(0, 5))
        Spinbox(departure_frame, from_=0, to=5, width=2, textvariable=self._departure_days)\
            .grid(row=1, column=2, padx=(0, 5))
        Label(departure_frame, text="jours, ", bg="LightSkyBlue1").grid(row=1, column=3, padx=(0, 5))
        Spinbox(departure_frame, from_=0, to=23, width=2, textvariable=self._departure_hours)\
            .grid(row=1, column=4, padx=(0, 5))
        Label(departure_frame, text="heures, ", bg="LightSkyBlue1").grid(row=1, column=5, padx=(0, 5))
        Spinbox(departure_frame, from_=0, to=59, width=2, textvariable=self._departure_minutes)\
            .grid(row=1, column=6, padx=(0, 5))
        Label(departure_frame, text="min", bg="LightSkyBlue1").grid(row=1, column=7, padx=(0, 5))

        Label(form, text="Nombre de voyageurs :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        Spinbox(form, from_=1, to=10, textvariable=self._travellers).pack(fill=BOTH, padx=(5, 150), pady=(0, 10))

        Label(form, text="Bagages :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        luggage_frame = Frame(form, bg="LightSkyBlue1")
        luggage_frame.pack(fill=BOTH, pady=(0, 10))
        Label(luggage_frame, text="Sac à dos", font=italic, bg="LightSkyBlue1", width=8).grid(row=1, column=1, padx=3)
        Label(luggage_frame, text="Sac à main", font=italic, bg="LightSkyBlue1", width=8).grid(row=1, column=2, padx=3)
        Label(luggage_frame, text="Valise", font=italic, bg="LightSkyBlue1", width=8).grid(row=1, column=3, padx=3)
        Label(luggage_frame, text="Encombrant", font=italic, bg="LightSkyBlue1", width=9).grid(row=1, column=4, padx=3)
        Spinbox(luggage_frame, from_=0, to=10, width=3, textvariable=self._backpack).grid(row=2, column=1, padx=15)
        Spinbox(luggage_frame, from_=0, to=10, width=3, textvariable=self._handbag).grid(row=2, column=2, padx=15)
        Spinbox(luggage_frame, from_=0, to=10, width=3, textvariable=self._suitcase).grid(row=2, column=3, padx=15)
        Spinbox(luggage_frame, from_=0, to=10, width=3, textvariable=self._bulky).grid(row=2, column=4, padx=15)

        Button(form, text="Calculer le meilleur itinéraire", font=bold, highlightbackground="LightSkyBlue1",
               command=self.start_calculation).pack(side=BOTTOM, pady=10)
        Button(form, text="Annuler le trajet", highlightbackground="LightSkyBlue1", command=self.cancel_ride,
               width=15).pack(side=LEFT, pady=(0, 15))
        Button(form, text="Sauvegarder le trajet", highlightbackground="LightSkyBlue1", command=self.save_ride,
               width=15).pack(side=RIGHT, pady=(0, 15))

        return form

    def save_ride(self):
        """ Essaye de créer un nouveau ride avec les données saisies dans le formulaire """

        if not self._start.get() or not self._end.get():
            showwarning('Saisie incorrecte', "Vous devez renseigner l'adresse de départ et l'adresse d'arrivée")
            return

        try:
            departure_time = time.time() + 10 \
                             + 3600 * 24 * self._departure_days.get() \
                             + 3600 * self._departure_hours.get() \
                             + 60 * self._departure_minutes.get()
            result = self._system.new_ride(self._start.get(), self._end.get(), departure_time)
            if not result["success"]:
                showerror('Echec de configuration du trajet', result["error"])
                return

            luggage = dict()
            if self._backpack.get() > 0:
                luggage[BACKPACK] = self._backpack.get()
            if self._handbag.get() > 0:
                luggage[HANDBAG] = self._handbag.get()
            if self._suitcase.get() > 0:
                luggage[SUITCASE] = self._suitcase.get()
            if self._bulky.get() > 0:
                luggage[BULKY] = self._bulky.get()
            result = self._system.set_ride_precisions(self._travellers.get(), luggage)
        except ValueError:
            showwarning('Saisie incorrecte', "Le contenu des spinbox doit être un nombre entier."
                                             "Aidez-vous des petites flêches pour incrémenter")
            return
        if not result["success"]:
            showerror('Paramêtrage incorrect', result["error"])
            return

        # Réactualise la page de formulaire (les adresses seront notemment transformées en points géographiques)
        self.init_parameters()

    def cancel_ride(self):
        """ Annulation du trajet sauvegardé et réactualisation de la page de formulaire """
        result = self._system.cancel_ride()
        if not result["success"]:
            showerror('Erreur système', result["error"])
            return
        self.pack_forget()
        RideSettingsPage(self._window, self._system)

    def start_calculation(self):
        """ Lance le calcul d'itinéraires et affiche les résultats en liste """
        from results import ResultsPage

        self.save_ride()
        result = self._system.start_calculation()
        if not result["success"]:
            showerror('Erreur système', result["error"])
            return

        possible_routes = result["possible_routes"]
        unsuitable_routes = result["unsuitable_routes"]

        self._frame.pack_forget()
        self._frame = ResultsPage(self, self._system.current_ride.weather, possible_routes, unsuitable_routes)
        self._frame.pack(fill=BOTH, expand=YES, side=RIGHT, padx=(0, 20), pady=20)
        self._frame.pack_propagate(0)

    def draw_result(self, route):
        """ Affichage de l'itinéraire souhaité par des points et des lignes droites sur la carte """

        # Nettoyage du précédent itinéraire dessiné
        self._map.delete('temp')

        # Références de la carte
        width, height = 600, 500
        dlat, dlong = 0.1128, 0.206
        ref_lat, ref_long = 48.9155, 2.2310

        # Transforme les coordonnées géographiques (lat, long) en coordonnées sur le plan de Paris (x, y)
        def get_map_coordinates(point):
            x = (point[1] - ref_long) / dlong * width
            y = (ref_lat - point[0]) / dlat * height
            return x, y

        start_x, start_y = get_map_coordinates(self._system.current_ride.start)
        end_x, end_y = get_map_coordinates(self._system.current_ride.end)

        # Dessiner les étapes de l'itinéraire
        stations = list()
        stations.append((start_x, start_y))
        walks = list()
        for step in route.steps:
            if step["mode"] == WALKING_MODE:
                walks.append(len(stations) - 1)
            elif step["mode"] in (BICYCLING_MODE, DRIVING_MODE):
                field = "position" if step["mode"] == BICYCLING_MODE else "geo_point"
                x1, y1 = get_map_coordinates(route.start_station[field])
                x2, y2 = get_map_coordinates(route.end_station[field])
                color = "green4" if step["mode"] == BICYCLING_MODE else "blue3"
                self._map.create_line(x1, y1, x2, y2, width=6, fill=color, tags="temp")
                stations.append((x1, y1))
                stations.append((x2, y2))

            elif step["mode"] == TRANSIT_MODE:
                x1, y1 = get_map_coordinates(step["details"]["start"]["position"])
                x2, y2 = get_map_coordinates(step["details"]["end"]["position"])
                try:
                    color = LINE_COLORS[step["details"]["line"]]
                except KeyError:
                    color = "navy"
                self._map.create_line(x1, y1, x2, y2, width=6, fill=color, tags="temp")
                stations.append((x1, y1))
                stations.append((x2, y2))
        for walk in walks:
            x1, y1 = stations[walk]
            if len(stations) > walk + 1:
                x2, y2 = stations[walk + 1]
            else:
                x2, y2 = end_x, end_y
            self._map.create_line(x1, y1, x2, y2, width=6, dash=(8, 4), fill="dodger blue", tags="temp")

        # Dessiner les stations traversées
        stations.append((end_x, end_y))
        for station in stations:
            x_pt = station[0]
            y_pt = station[1]
            self._map.create_oval(x_pt - 5, y_pt - 5, x_pt + 5, y_pt + 5, width=1, fill="white", tags="temp")
