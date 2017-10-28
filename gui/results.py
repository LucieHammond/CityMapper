# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
from routes import bicycling, driving, transit


class WeatherFrame(LabelFrame):

    def __init__(self, window, weather):
        LabelFrame.__init__(self, window, text="Conditions météorologiques", bg="LightSkyBlue1")
        self._weather = weather

        self._temperature = PhotoImage(file="../resources/temp.gif")
        self._rain = PhotoImage(file="../resources/rain.gif")
        self._wind = PhotoImage(file="../resources/wind.gif")
        self._snow = PhotoImage(file="../resources/snow.gif")
        self.display_forecast()

    def display_forecast(self):
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

        Label(self, text="%d°C" % self._weather["temperature"], bg="LightSkyBlue1").grid(row=2, column=1, pady=(0,2))
        Label(self, text=rain_text, bg="LightSkyBlue1").grid(row=2, column=2, pady=(0,2))
        Label(self, text="%.1fm/s" % self._weather["wind"], bg="LightSkyBlue1").grid(row=2, column=3, pady=(0,2))
        Label(self, text=snow_text, bg="LightSkyBlue1").grid(row=2, column=4, pady=(0,2))


class ResultFrame(Frame):

    velib = PhotoImage(file="../resources/velib.gif")
    autolib = PhotoImage(file="../resources/autolib.gif")
    subway = PhotoImage(file="../resources/subway.gif")
    walk = PhotoImage(file="../resources/walk.gif")

    def __init__(self, window, route):
        Frame.__init__(self, window, width=340, height=80, highlightbackground="black", highlightthickness=1)
        self._route = route

        self.display_recap()

    def display_recap(self):

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

        if self._route.distance > 1000:
            dist = "%.1f km" % (self._route.distance / 1000.0)
        else:
            dist = "%d m" % self._route.distance

        price = "─ %.2f€" % self._route.price
        walk = "%dmin à pied" % int(round(self._route.walking_time / 60.0))
        transfers = "%d ↔" % self._route.transfers_nb

        if self._route.weather_impact < -30: weather = "Météo: ++"
        elif self._route.weather_impact < 0: weather = "Météo: +"
        elif self._route.weather_impact < 20: weather = "Météo: /"
        elif self._route.weather_impact < 50: weather = "Météo: -"
        else: weather = "Météo: --"

        if self._route.difficulty == 0: difficulty = "Charges: +"
        elif self._route.difficulty <= 20: difficulty = "Charges: /"
        elif self._route.difficulty <= 50: difficulty = "Charges: -"
        else: difficulty = "Charges: --"

        first_line = Frame(self, width=340, height=40)
        icon = Canvas(first_line, width=35, height=35, highlightthickness=0)
        icon.create_image(0, 0, anchor=NW, image=image)
        icon.grid(row=1, column=1, padx=(13, 5), pady=3)
        Label(first_line, text="%s (%s)" % (time, dist), font=("Helvetica", 18, "normal"), anchor=E, width=16)\
            .grid(row=1, column=2, pady=7)
        Label(first_line, text=price, font=(None, 14, "italic"), width=7).grid(row=1, column=3, pady=7)
        Button(first_line, text=">", font=("Helvetica", 16, "bold"), width=1).grid(row=1, column=4, padx=5, pady=7)
        first_line.pack(fill=BOTH, expand=YES)

        second_line = Frame(self, width=340, height=50)
        Label(second_line, text=walk, font=(None, 14, "italic"), width=10)\
            .grid(row=1, column=1, padx=(10,0), pady=(0,5))
        Label(second_line, text=transfers, font=(None, 14, "italic"), width=4).grid(row=1, column=2, pady=(0,5))
        Label(second_line, text=weather, font=(None, 14, "italic"), width=9).grid(row=1, column=3, pady=(0,5))
        Label(second_line, text=difficulty, font=(None, 14, "italic"), width=9).grid(row=1, column=4, pady=(0,5))
        second_line.pack(fill=BOTH, expand=YES)


class ResultsPage(Frame):

    def __init__(self, window, weather, good_routes, bad_routes):
        Frame.__init__(self, window, bg="snow")

        self._window = window
        self._good_routes = good_routes
        self._bad_routes = bad_routes

        WeatherFrame(self, weather).pack(side=TOP, fill=X, expand=YES)
        results = Frame(self, height=500, bg="LightSkyBlue1")
        results.pack(side=TOP, fill=BOTH, expand=YES)
        results.pack_propagate(0)
        Label(results, text="-- Résultats --", font=("Helvetica", 18, "bold"), bg="LightSkyBlue1").pack(pady=(20, 10))
        if len(self._good_routes) > 0:
            Label(results, text="Itinéraire recommandé", fg="gray25", bg="snow2", anchor=W, highlightbackground="black", highlightthickness=1)\
                .pack(fill=BOTH)
            best_result = ResultFrame(results, self._good_routes[0])
            best_result.pack(fill=BOTH)
        if len(self._good_routes) > 1:
            Label(results, text="Autres itinéraires possibles", fg="gray25", bg="snow2", anchor=W, highlightbackground="black", highlightthickness=1) \
                .pack(fill=BOTH)
            for route in self._good_routes[1:]:
                result = ResultFrame(results, route)
                result.pack(fill=BOTH)
        if len(self._bad_routes) > 0:
            Label(results, text="Itinéraires non retenus", fg="gray25", bg="snow2", anchor=W, highlightbackground="black", highlightthickness=1) \
                .pack(fill=BOTH)
            for route in bad_routes:
                bad_result = self.unsuitable_route(results, route)
                bad_result.pack(fill=BOTH)

        Button(results, text="Nouveau trajet", highlightbackground="LightSkyBlue1", width=20, command=self.new_ride)\
            .pack(side=BOTTOM, pady=(20,0))
        Frame(results, height=400, bg="snow2", highlightbackground="black", highlightthickness=1).pack(fill=BOTH)

    def unsuitable_route(self, window, route):
        frame = Frame(window, width=340, highlightbackground="black", highlightthickness=1)

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
        Label(frame, text=message, font=(None, 12, "normal")).grid(row=1, column=2)
        return frame

    def new_ride(self):
        self._window.cancel_ride()
