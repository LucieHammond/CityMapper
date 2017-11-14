# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
from routes import bicycling, driving, transit
from constants import WALKING_MODE, BICYCLING_MODE, DRIVING_MODE, TRANSIT_MODE, LINE_COLORS, OSX


class WeatherFrame(LabelFrame):
    """ Frame dédié à l'affichage des informations météorologiques """

    def __init__(self, parent, weather):
        LabelFrame.__init__(self, parent, text="Conditions météorologiques", bg="LightSkyBlue1")
        self._weather = weather

        # Icons Météo
        self._temperature = PhotoImage(file="resources/temp.gif")
        self._rain = PhotoImage(file="resources/rain.gif")
        self._wind = PhotoImage(file="resources/wind.gif")
        self._snow = PhotoImage(file="resources/snow.gif")
        self.display_forecast()

    def display_forecast(self):
        """ Inclut et affiche les données météo dans le LabelFrame"""
        temp = Canvas(self, width=45, height=45, highlightthickness=0, bg="LightSkyBlue1")
        temp.create_image(0, 0, anchor=NW, image=self._temperature)
        temp.grid(row=1, column=1, padx=18, pady=(7, 3))
        rain = Canvas(self, width=45, height=45, highlightthickness=0, bg="LightSkyBlue1")
        rain.create_image(0, 0, anchor=NW, image=self._rain)
        rain.grid(row=1, column=2, padx=18, pady=(7, 3))
        wind = Canvas(self, width=45, height=45, highlightthickness=0, bg="LightSkyBlue1")
        wind.create_image(0, 0, anchor=NW, image=self._wind)
        wind.grid(row=1, column=3, padx=18, pady=(7, 3))
        snow = Canvas(self, width=45, height=45, highlightthickness=0, bg="LightSkyBlue1")
        snow.create_image(0, 0, anchor=NW, image=self._snow)
        snow.grid(row=1, column=4, padx=18, pady=(7, 3))

        rain_text = "%dmm/3h" % self._weather["rain"] if round(self._weather["rain"], 1) else "--"
        snow_text = "%dmm/3h" % self._weather["snow"] if round(self._weather["snow"], 1) else "--"

        Label(self, text="%d°C" % self._weather["temperature"], bg="LightSkyBlue1").grid(row=2, column=1, pady=(0, 2))
        Label(self, text=rain_text, bg="LightSkyBlue1").grid(row=2, column=2, pady=(0, 2))
        Label(self, text="%.1fm/s" % self._weather["wind"], bg="LightSkyBlue1").grid(row=2, column=3, pady=(0, 2))
        Label(self, text=snow_text, bg="LightSkyBlue1").grid(row=2, column=4, pady=(0, 2))


class ResultFrame(Frame):
    """ Frame dédié à l'affichage d'un itinéraire trouvé (résumé et détails)"""

    # Icons flat des transports
    velib = PhotoImage(file="resources/velib.gif")
    autolib = PhotoImage(file="resources/autolib.gif")
    subway = PhotoImage(file="resources/subway.gif")
    walk = PhotoImage(file="resources/walk.gif")

    def __init__(self, parent, route, new_details_frame):
        Frame.__init__(self, parent, width=340, highlightbackground="black", highlightthickness=1)
        self._route = route
        self._new_details_frame = new_details_frame

        first_line, second_line = self.recap_lines(True)
        first_line.pack(fill=BOTH, expand=YES)
        second_line.pack(fill=BOTH, expand=YES)

    def recap_lines(self, with_button, frame=None):
        """ Crée et renvoie un récapitulatif de l'itinéraire sous forme de deux lignes (frame) à insérer

        :param with_button: booléen indiquant si l'on ajoute (ou non) un bouton flêché à droite de la 1ère ligne
        :param frame: le frame parent dans lequel les lignes seront insérées (par défaut self)
        :return: les deux lignes d'informations (de type frame)
        """
        if not frame:
            frame = self

        # Récupérer les données à afficher
        if isinstance(self._route, bicycling.VelibRoute): image = ResultFrame.velib
        elif isinstance(self._route, driving.AutolibRoute): image = ResultFrame.autolib
        elif isinstance(self._route, transit.SubwayRoute) and self._route.is_walking_route(): image = ResultFrame.walk
        else: image = ResultFrame.subway

        hours = (self._route.time + 30) // 3600
        minutes = ((self._route.time + 30) % 3600) // 60
        if hours != 0:
            time = "%dh %dmin" % (hours, minutes)
        else:
            time = "%dmin" % minutes

        if self._route.distance >= 1000:
            dist = "%.1f km" % (self._route.distance / 1000.0)
        else:
            dist = "%d m" % self._route.distance

        price = "─ %.2f€" % self._route.price
        walk = "%dmin à pied" % int(round(self._route.walking_time / 60.0))
        transfers = "%d ↔" % self._route.transfers_nb

        if self._route.weather_impact <= -30: weather = "Météo: ++"
        elif self._route.weather_impact <= 0: weather = "Météo: +"
        elif self._route.weather_impact <= 30: weather = "Météo: /"
        elif self._route.weather_impact <= 90: weather = "Météo: -"
        else: weather = "Météo: --"

        if self._route.difficulty == 0: difficulty = "Charges: +"
        elif self._route.difficulty <= 25: difficulty = "Charges: /"
        elif self._route.difficulty <= 50: difficulty = "Charges: -"
        else: difficulty = "Charges: --"

        italic = ("Lucida", 14, "italic") if OSX else ("Calibri", 10, "italic")
        big = ("Helvetica", 18, "normal") if OSX else ("Helvetica", 14, "normal")
        bold = ("Helvetica", 16, "bold") if OSX else ("Helvetica", 12, "bold")

        # Première ligne récapitulative
        first_line = Frame(frame, width=340, height=40)
        icon = Canvas(first_line, width=35, height=35, highlightthickness=0)
        icon.create_image(0, 0, anchor=NW, image=image)
        icon.grid(row=1, column=1, padx=(13, 5), pady=3)
        Label(first_line, text="%s (%s)" % (time, dist), font=big, anchor=E, width=16)\
            .grid(row=1, column=2, pady=7)
        Label(first_line, text=price, font=italic, width=7).grid(row=1, column=3, pady=7)
        if with_button:
            Button(first_line, text=">", font=bold, width=1, command=self.display_details)\
                .grid(row=1, column=4, padx=5, pady=7)

        # Deuxième ligne récapitulative
        second_line = Frame(frame, width=340, height=50)
        Label(second_line, text=walk, font=italic, width=10)\
            .grid(row=1, column=1, padx=(8, 0), pady=(0, 5))
        Label(second_line, text=transfers, font=italic, width=4).grid(row=1, column=2, pady=(0, 5))
        Label(second_line, text=weather, font=italic, width=9).grid(row=1, column=3, pady=(0, 5))
        Label(second_line, text=difficulty, font=italic, width=9).grid(row=1, column=4, pady=(0, 5))

        return first_line, second_line

    def display_details(self):
        """ Affiche les détails de l'itinéraire quand celui-ci a été sélectionné """

        # Appelle la méthode 'new_details_frame' du ResultsPage qui remplace la liste des itinéraires par un frame
        # de présentation détaillée et qui demande l'affichage sur la carte de l'itinéraire passé en paramètre
        # On récupère le frame de détail ainsi créé dans la variable frame pour le remplir précisément
        frame = self._new_details_frame(self._route)

        # Ajouter les 2 lignes de résumé à ce nouveau frame
        first_recap, second_recap = self.recap_lines(False, frame=frame)
        first_recap.configure(relief=SUNKEN, borderwidth=1)
        second_recap.configure(relief=RAISED, borderwidth=1)
        first_recap.pack(fill=BOTH, expand=YES)
        second_recap.pack(fill=BOTH, expand=YES)

        # Calculer la hauteur nécessaire à la présentation détaillée des instructions
        height = 20 + 10 * (len(self._route.steps) + 1)
        height += sum([90 for step in self._route.steps if step["mode"] == WALKING_MODE])
        height += sum([110 for step in self._route.steps if step["mode"] == TRANSIT_MODE])
        height += sum([130 for step in self._route.steps if step["mode"] in (BICYCLING_MODE, DRIVING_MODE)])
        side_line = Canvas(frame, width=40, height=height, highlightthickness=0)
        side_line.pack(side=LEFT, padx=(10, 0), pady=10)
        yline = 15
        next_station = None

        # Fonts
        normal = ("Helvetica", 12, "normal") if OSX else ("Helvetica", 9, "normal")
        bold = ("Helvetica", 14, "bold") if OSX else ("Helvetica", 11, "bold")
        italic = ("Helvetica", 12, "italic") if OSX else ("Helvetica", 8, "italic")
        small = ("Calibri", 8, "normal") if OSX else ("Calibri", 5, "normal")
        small_italic = ("Helvetica", 10, "italic") if OSX else ("Helvetica", 8, "italic")

        # Départ
        if len(self._route.steps) == 0:
            side_line.create_oval(10, yline - 5, 20, yline + 5, width=3)
            station = Label(frame, text="Départ = Arrivée", font=bold, anchor=W)
            station.pack(fill=BOTH, pady=(15, 0))
            pady_start = 0
            next_station = station
        elif self._route.steps[0]["mode"] == WALKING_MODE:
            side_line.create_oval(10, yline-5, 20, yline+5, width=3)
            station = Label(frame, text="Départ", font=bold, anchor=W)
            station.pack(fill=BOTH, pady=(15, 0))
            pady_start = 0
            next_station = station
        else:
            pady_start = 13

        # Affichage de chaque étape
        for step in self._route.steps:

            time = "%d min" % ((step["time"] + 30) // 60)
            dist = "%.1f km" % (step["dist"] / 1000.0) if step["dist"] >= 1000 else "%d m" % step["dist"]

            if step["mode"] == WALKING_MODE:
                assert next_station
                side_line.create_line(15, yline+15, 15, yline+90, width=6, dash=(6, 10), fill="SlateGray2")
                side_line.create_image(15, yline+33, anchor=NW, image=ResultFrame.walk)
                walk_text = "Marchez sur %s (%s)" % (dist, time)
                Label(frame, text=walk_text, font=italic, anchor=W).pack(fill=BOTH, pady=28, padx=5)

                next_station = None
                yline += 100

            elif step["mode"] == BICYCLING_MODE:
                assert not next_station
                side_line.create_line(15, yline, 15, yline+140, width=12, fill="green4")
                side_line.create_image(0, yline+50, anchor=NW, image=ResultFrame.velib)
                side_line.create_oval(10, yline-5, 20, yline+5, width=2, outline="green4", fill="pale green")
                side_line.create_oval(10, yline+135, 20, yline+145, width=2, outline="green4", fill="pale green")

                station1_name = self._route.start_station["name"].split(" - ")[1].capitalize()
                station1_address = self._route.start_station["address"].capitalize()
                if "places" in self._route.start_station:
                    station1_details = " - - - >  %d %s %s" % (
                        self._route.start_station["places"],
                        "vélo disponible" if self._route.start_station["places"] == 1 else "vélos disponibles",
                        "(station bonus)" if self._route.start_station["bonus"] else "")
                else:
                    station1_details = " - - - > dans la limite des disponibilités futures %s" % (
                        "(station bonus)" if self._route.start_station["bonus"] else "")
                Label(frame, text=station1_name, font=bold, anchor=W).pack(fill=BOTH, pady=(pady_start, 0))
                Label(frame, text=station1_address, font=small_italic, anchor=W).pack(fill=BOTH)
                Label(frame, text=station1_details, font=small, anchor=W).pack(fill=BOTH)

                bike_text = "Pédalez sur %s (%s)" % (dist, time)
                Label(frame, text=bike_text, font=italic, anchor=W).pack(fill=BOTH, pady=17, padx=5)

                station2_name = self._route.end_station["name"].split(" - ")[1].capitalize()
                station2_address = self._route.end_station["address"].capitalize()
                if "places" in self._route.start_station:
                    station2_details = " - - - >  %d %s %s" % (
                        self._route.end_station["places"],
                        "place disponible" if self._route.end_station["places"] == 1 else "places disponibles",
                        "(station bonus)" if self._route.end_station["bonus"] else "")
                else:
                    station2_details = " - - - > dans la limite des disponibilités futures %s" % (
                        "(station bonus)" if self._route.start_station["bonus"] else "")
                station = Label(frame, text=station2_name, font=bold, anchor=W)
                station.pack(fill=BOTH)
                Label(frame, text=station2_address, font=small_italic, anchor=W).pack(fill=BOTH)
                Label(frame, text=station2_details, font=small, anchor=W).pack(fill=BOTH)

                next_station = station
                yline += 140

            elif step["mode"] == DRIVING_MODE:
                assert not next_station
                side_line.create_line(15, yline, 15, yline+140, width=12, fill="blue3")
                side_line.create_image(0, yline+50, anchor=NW, image=ResultFrame.autolib)
                side_line.create_oval(10, yline-5, 20, yline+5, width=2, outline="blue3", fill="light blue")
                side_line.create_oval(10, yline+135, 20, yline+145, width=2, outline="blue3", fill="light blue")

                station1_name = self._route.start_station["public_name"]
                station1_address = self._route.start_station["address"]
                if "places" in self._route.start_station:
                    station1_details = " - - - >  %d %s" % (
                        self._route.start_station["places"],
                        "voiture disponible" if self._route.start_station["places"] == 1 else "voitures disponibles")
                else:
                    station1_details = " - - - dans la limite des disponibilités futures - - -"
                Label(frame, text=station1_name, font=bold, anchor=W).pack(fill=BOTH, pady=(pady_start, 0))
                Label(frame, text=station1_address, font=small_italic, anchor=W).pack(fill=BOTH)
                Label(frame, text=station1_details, font=small, anchor=W).pack(fill=BOTH)

                drive_text = "Conduisez sur %s (%s)" % (dist, time)
                Label(frame, text=drive_text, font=italic, anchor=W).pack(fill=BOTH, pady=17, padx=5)

                station2_name = self._route.end_station["public_name"]
                station2_address = self._route.end_station["address"]
                if "places" in self._route.end_station:
                    station2_details = " - - - >  %d %s" % (
                        self._route.end_station["places"],
                        "place disponible" if self._route.end_station["places"] == 1 else "places disponibles")
                else:
                    station2_details = " - - - dans la limite des disponibilités futures - - -"
                station = Label(frame, text=station2_name, font=bold, anchor=W)
                station.pack(fill=BOTH)
                Label(frame, text=station2_address, font=small_italic, anchor=W).pack(fill=BOTH)
                Label(frame, text=station2_details, font=small, anchor=W).pack(fill=BOTH)

                next_station = station
                yline += 140

            elif step["mode"] == TRANSIT_MODE:

                try:
                    color = LINE_COLORS[step["details"]["line"]]
                except KeyError:
                    color = "navy"
                side_line.create_line(15, yline, 15, yline + 120, width=12, fill=color)
                side_line.create_oval(10, yline - 5, 20, yline + 5, width=2, outline=color, fill="white")
                side_line.create_oval(10, yline + 115, 20, yline + 125, width=2, outline=color, fill="white")

                if not next_station:
                    station1_name = "%s (%s)" % (step["details"]["start"]["name"], step["details"]["line"])
                    Label(frame, text=station1_name, font=bold, anchor=W).pack(fill=BOTH, pady=(pady_start + 2, 0))
                else:
                    add_on = ' => %s' % step["details"]["line"]
                    next_station["text"] = next_station["text"][:-1] + add_on + ')'

                line_text = "Ligne %s direction %s" % (step["details"]["line"], step["details"]["direction"])
                transit_text = "%d arrêt%s (%s sur %s)" % (
                    step["details"]["stops"], "s" if step["details"]["stops"] > 1 else "", time, dist)
                Label(frame, text=line_text, font=normal, anchor=W).pack(fill=BOTH)
                Label(frame, text=transit_text, font=italic, anchor=W).pack(fill=BOTH, pady=(26, 30), padx=5)

                station2_name = "%s (%s)" % (step["details"]["end"]["name"], step["details"]["line"])
                station = Label(frame, text=station2_name, font=bold, anchor=W)
                station.pack(fill=BOTH, pady=(0, 2))

                next_station = station
                yline += 120

            pady_start = 0

        # Arrivée
        if not next_station:
            side_line.create_oval(10, yline-5, 20, yline+5, width=3)
            Label(frame, text="Arrivée", font=bold, anchor=W).pack(fill=BOTH, pady=2)


class ResultsPage(Frame):
    """ Page d'affichage des résultats de la simulation """

    def __init__(self, parent, weather, good_routes, bad_routes):
        Frame.__init__(self, parent, bg="LightSkyBlue1")

        self._parent = parent
        self._good_routes = good_routes
        self._bad_routes = bad_routes

        WeatherFrame(self, weather).pack(side=TOP, fill=X, expand=YES)
        title = ("Helvetica", 18, "bold") if OSX else ("Helvetica", 16, "bold")
        Label(self, text="-- Résultats --", font=title, bg="LightSkyBlue1")\
            .pack(side=TOP, fill=BOTH, pady=(20, 10))

        self._results = Frame(self, bg="snow2", highlightbackground="black", highlightthickness=1, height=315)
        self._details = Frame(self, highlightbackground="black", highlightthickness=1, height=315)

        self.set_results_list()
        self.display_results_list()

        Button(self, text="Nouveau trajet", highlightbackground="LightSkyBlue1", width=20, command=self.new_ride)\
            .pack(side=BOTTOM, pady=(20, 0))

    def set_results_list(self):
        """ Créer et afficher la liste ordonnée des itinéraires dans le frame self._results (selon 3 catégories) """
        if len(self._good_routes) > 0:
            Label(self._results, text="Itinéraire recommandé", fg="gray25", bg="snow2", anchor=W)\
                .pack(padx=10, pady=2, fill=BOTH)
            best_result = ResultFrame(self._results, self._good_routes[0], self.new_details_frame)
            best_result.pack(fill=BOTH)
        if len(self._good_routes) > 1:
            Label(self._results, text="Autres itinéraires possibles", fg="gray25", bg="snow2", anchor=W) \
                .pack(padx=10, pady=2, fill=BOTH)
            for route in self._good_routes[1:]:
                result = ResultFrame(self._results, route, self.new_details_frame)
                result.pack(fill=BOTH)
        if len(self._bad_routes) > 0:
            Label(self._results, text="Itinéraires non retenus", fg="gray25", bg="snow2", anchor=W) \
                .pack(padx=10, pady=2, fill=BOTH)
            for route in self._bad_routes:
                bad_result = self.unsuitable_route(self._results, route)
                bad_result.pack(fill=BOTH)

    def display_results_list(self):
        """ Affiche la liste des résultats qui se trouve dans le frame self._results """
        self._details.pack_forget()
        self._results.pack(side=TOP, fill=BOTH, expand=YES)
        self._results.pack_propagate(0)

    @staticmethod
    def unsuitable_route(parent, route):
        """ Créer et renvoyer un frame de description pour un mode de transport 'route' non retenu """
        frame = Frame(parent, width=340, highlightbackground="black", highlightthickness=1)

        # Répartir le texte du message d'erreur sur plusieurs lignes pour ne pas qu'il dépasse sur les côtés
        message = route["msg"]
        for k in range(0, len(route["msg"]) // 45):
            i = 45 * (k + 1)
            while i > 45 * k:
                if route["msg"][i] == " ":
                    message = message[:i] + "\n" + message[i+1:]
                    break
                i -= 1

        images_dict = {"velib": ResultFrame.velib, "autolib": ResultFrame.autolib, "transit": ResultFrame.subway}
        image = images_dict[route["mode"]]

        icon = Canvas(frame, width=35, height=35, highlightthickness=0)
        icon.create_image(0, 0, anchor=NW, image=image)
        icon.grid(row=1, column=1, padx=13, pady=3)
        font = ("Lucida", 12, "normal") if OSX else ("Calibri", 10, "normal")
        Label(frame, text=message, font=font).grid(row=1, column=2)
        return frame

    def new_details_frame(self, route):
        """ Créer et renvoyer un nouveau frame de detail scrollable avec bouton de retour
        pour contenir les informations détaillées d'un itinéraire à suivre """

        self._results.pack_forget()

        # Réponse aux évênements de scroll
        def configuration(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        self._details = Frame(self, highlightbackground="black", highlightthickness=1, height=315)
        self._details.pack(side=TOP, fill=BOTH, expand=YES)
        self._details.pack_propagate(0)

        canvas = Canvas(self._details)
        frame = Frame(canvas)
        scrollbar = Scrollbar(self._details, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        canvas.pack_propagate(0)
        canvas.create_window((0, 0), window=frame, anchor=NW)
        frame.bind("<Configure>", configuration)

        header = Frame(frame, bg="snow2", height=45, width=340)
        header.pack(fill=BOTH, expand=YES)
        header.pack_propagate(0)
        font = ("Helvetica", 20, "bold") if OSX else ("Helvetica", 16, "bold")
        Button(header, text="<", font=font, width=1, highlightbackground="snow2",
               command=self.display_results_list).pack(padx=10, side=LEFT)

        # Demander au frame parent (Settings) d'afficher l'itinéraire sur la carte
        self._parent.draw_result(route)
        return frame

    def new_ride(self):
        """ Revenir à la page de définition d'un nouveau trajet avec les champs du formulaire vides """
        self._parent.cancel_ride()
