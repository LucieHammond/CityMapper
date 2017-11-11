# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
from routes import bicycling, driving, transit
from constants import WALKING_MODE, BICYCLING_MODE, DRIVING_MODE, TRANSIT_MODE, LINE_COLORS


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

    def __init__(self, window, route, new_details_frame):
        Frame.__init__(self, window, width=340, highlightbackground="black", highlightthickness=1)
        self._route = route
        self._new_details_frame = new_details_frame

        first_line, second_line = self.recap_lines(True)
        first_line.pack(fill=BOTH, expand=YES)
        second_line.pack(fill=BOTH, expand=YES)

    def recap_lines(self, with_button, frame=None):
        if not frame:
            frame = self

        # Get recap data
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

        if self._route.weather_impact < -30: weather = "Météo: ++"
        elif self._route.weather_impact < 0: weather = "Météo: +"
        elif self._route.weather_impact < 20: weather = "Météo: /"
        elif self._route.weather_impact < 50: weather = "Météo: -"
        else: weather = "Météo: --"

        if self._route.difficulty == 0: difficulty = "Charges: +"
        elif self._route.difficulty <= 20: difficulty = "Charges: /"
        elif self._route.difficulty <= 50: difficulty = "Charges: -"
        else: difficulty = "Charges: --"

        # Recap first line
        first_line = Frame(frame, width=340, height=40)
        icon = Canvas(first_line, width=35, height=35, highlightthickness=0)
        icon.create_image(0, 0, anchor=NW, image=image)
        icon.grid(row=1, column=1, padx=(13, 5), pady=3)
        Label(first_line, text="%s (%s)" % (time, dist), font=("Helvetica", 18, "normal"), anchor=E, width=16)\
            .grid(row=1, column=2, pady=7)
        Label(first_line, text=price, font=(None, 14, "italic"), width=7).grid(row=1, column=3, pady=7)
        if with_button:
            Button(first_line, text=">", font=("Helvetica", 16, "bold"), width=1, command=self.display_details)\
                .grid(row=1, column=4, padx=5, pady=7)

        # Recap second line
        second_line = Frame(frame, width=340, height=50)
        Label(second_line, text=walk, font=(None, 14, "italic"), width=10)\
            .grid(row=1, column=1, padx=(8,0), pady=(0,5))
        Label(second_line, text=transfers, font=(None, 14, "italic"), width=4).grid(row=1, column=2, pady=(0,5))
        Label(second_line, text=weather, font=(None, 14, "italic"), width=9).grid(row=1, column=3, pady=(0,5))
        Label(second_line, text=difficulty, font=(None, 14, "italic"), width=9).grid(row=1, column=4, pady=(0,5))

        return first_line, second_line

    def display_details(self):
        print self._route.steps

        frame = self._new_details_frame(self._route)

        first_recap, second_recap = self.recap_lines(False, frame=frame)
        first_recap.configure(relief=SUNKEN, borderwidth=1)
        second_recap.configure(relief=RAISED, borderwidth=1)
        first_recap.pack(fill=BOTH, expand=YES)
        second_recap.pack(fill=BOTH, expand=YES)

        height = 20 + 10 * (len(self._route.steps) + 1)
        height += sum([90 for step in self._route.steps if step["mode"] == WALKING_MODE])
        height += sum([110 for step in self._route.steps if step["mode"] == TRANSIT_MODE])
        height += sum([130 for step in self._route.steps if step["mode"] in (BICYCLING_MODE, DRIVING_MODE)])
        side_line = Canvas(frame, width=40, height=height, highlightthickness=0)
        side_line.pack(side=LEFT, padx=(10, 0), pady=10)
        yline = 15
        next_station = None

        # Fonts
        normal = ("Helvetica", 12, "normal")
        bold = ("Helvetica", 14, "bold")
        italic = ("Helvetica", 12, "italic")
        small = ("Colibri", 8, "normal")
        small_italic = ("Helvetica", 10, "italic")

        # Départ
        if self._route.steps[0]["mode"] == WALKING_MODE:
            side_line.create_oval(10, yline-5, 20, yline+5, width=3)
            station = Label(frame, text="Départ", font=bold, anchor=W)
            station.pack(fill=BOTH, pady=(15, 0))
            pady_start = 0
            next_station = station
        else:
            pady_start = 13

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
                    add_on = ' => %s' % step["details"]["start"]["line"]
                    next_station["text"] = next_station["text"].split(')')[0] + add_on

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

    def __init__(self, window, weather, good_routes, bad_routes):
        Frame.__init__(self, window, bg="LightSkyBlue1")

        self._window = window
        self._good_routes = good_routes
        self._bad_routes = bad_routes

        WeatherFrame(self, weather).pack(side=TOP, fill=X, expand=YES)
        Label(self, text="-- Résultats --", font=("Helvetica", 18, "bold"), bg="LightSkyBlue1")\
            .pack(side=TOP, fill=BOTH, pady=(20,10))

        self._results = Frame(self, bg="snow2", highlightbackground="black", highlightthickness=1, height=315)
        self._details = Frame(self, highlightbackground="black", highlightthickness=1, height=315)

        self.set_results_list()
        self.display_results_list()

        Button(self, text="Nouveau trajet", highlightbackground="LightSkyBlue1", width=20, command=self.new_ride)\
            .pack(side=BOTTOM, pady=(20,0))

    def set_results_list(self):
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
        self._details.pack_forget()
        self._results.pack(side=TOP, fill=BOTH, expand=YES)
        self._results.pack_propagate(0)

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

    def new_details_frame(self, route):

        self._results.pack_forget()

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
        Button(header, text="<", font=("Helvetica", 20, "bold"), width=1, highlightbackground="snow2", command=self.display_results_list)\
            .pack(padx=10, side=LEFT)

        self._window.draw_result(route)
        return frame

    def new_ride(self):
        self._window.cancel_ride()


if __name__ == "__main__":
    main_window = Tk()
    from core.system import HowToGoSystem
    main_window.title("Comment y aller ?")
    system = HowToGoSystem()
    page = ResultsPage(main_window,
                       {"temperature": 21, "wind": 5.3, "rain": 2.8, "snow": 0},
                       [],
                       [{"mode": "velib", "msg": "Vos bagages sont trop encombrants pour vous permettre de prendre le velib"}])
    page.pack(fill=BOTH, expand=YES, side=RIGHT, padx=(0, 20), pady=20)
    page.pack_propagate(0)
    main_window.resizable(0, 0)
    main_window.mainloop()