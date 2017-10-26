# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
from core.system import HowToGoSystem
from datetime import date
import time
from constants import BACKPACK, HANDBAG, SUITCASE, BULKY


class RideSettingsPage(Frame):

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
        if self._system.current_ride:
            ride = self._system.current_ride
            print ride.start[0], ride.start[1]
            self._start.set('$ %d,%d' % (ride.start[0], ride.start[1]))
            self._end.set('$ %d,%d' % (ride.end[0], ride.end[1]))
            time_diff = int(ride.departure_time - time.time())
            self._departure_days.set(max(0, time_diff // (3600*24)))
            self._departure_hours.set(max(0, (time_diff % 3600*24) // 3600))
            self._departure_minutes.set(max(0, round((time_diff % 3600) / 60.0 )))

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

        # Le menubar de tkinter ne fonctionne pas sur Mac OS X. Je simule donc un menu à la main
        menubar = Frame(self, height=30, bg="SlateGray3", relief=RAISED, borderwidth=2)
        menubar.pack(fill=BOTH)
        Label(menubar, text="%s :" % self._system.current_user.username, font=(None, 14, "bold"), bg="SlateGray3")\
            .pack(side=LEFT, padx=(10, 5))
        Button(menubar, text="Mon profil", highlightbackground="SlateGray3", command=self.display_profile_1)\
            .pack(side=LEFT, padx=5)
        Button(menubar, text="Mes préférences", highlightbackground="SlateGray3", command=self.display_profile_2)\
            .pack(side=LEFT, padx=5)
        Button(menubar, text="Deconnexion", highlightbackground="SlateGray3", command=self.deconnection)\
            .pack(side=RIGHT, padx=5)
        self._window.config(menu=menubar)

    def display_map(self):
        self._map = Canvas(self, width=600, height=500, highlightthickness=0)
        self._image = PhotoImage(file="../resources/map.gif")
        self._map.create_image(0, 0, anchor=NW, image=self._image)
        self._map.pack(side=LEFT, padx=20, pady=35)

    def display_profile_1(self):
        from profile import ProfilePage
        self.pack_forget()
        ProfilePage(self._window, self._system, 1)

    def display_profile_2(self):
        from profile import ProfilePage
        self.pack_forget()
        ProfilePage(self._window, self._system, 2)

    def deconnection(self):
        from home import HomePage
        result = self._system.sign_out()
        if not result["success"]:
            showerror('Erreur système', result["error"])
            return
        self.pack_forget()
        HomePage(self._window, self._system)

    def settings_form(self):
        form = Frame(self, bg="LightSkyBlue1")

        Label(form, text="-- Nouveau trajet --", font=("Helvetica", 18, "bold"), bg="LightSkyBlue1").pack(pady=(5,10))
        italic = (None, 13, "italic")
        bold = (None, 14, "bold")

        Label(form, text="Départ :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        Entry(form, textvariable=self._start, width=40).pack(padx=5, pady=(0,10))

        Label(form, text="Arrivée :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        Entry(form, textvariable=self._end, width=40).pack(padx=5, pady=(0,10))

        Label(form, text="Moment du départ :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        departure_frame = Frame(form, bg="LightSkyBlue1")
        departure_frame.pack(padx=5, pady=(0,10))
        Label(departure_frame, text="Dans", bg="LightSkyBlue1").grid(row=1, column=1, padx=(0,5))
        Spinbox(departure_frame, from_=0, to=5, width=2, textvariable=self._departure_days).grid(row=1, column=2, padx=(0,5))
        Label(departure_frame, text="jours, ", bg="LightSkyBlue1").grid(row=1, column=3, padx=(0, 5))
        Spinbox(departure_frame, from_=0, to=23, width=2, textvariable=self._departure_hours).grid(row=1, column=4, padx=(0,5))
        Label(departure_frame, text="heures, ", bg="LightSkyBlue1").grid(row=1, column=5, padx=(0,5))
        Spinbox(departure_frame, from_=0, to=59, width=2, textvariable=self._departure_minutes).grid(row=1, column=6, padx=(0,5))
        Label(departure_frame, text="min", bg="LightSkyBlue1").grid(row=1, column=7, padx=(0,5))

        Label(form, text="Nombre de voyageurs :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        Spinbox(form, from_=0, to=10, textvariable=self._travellers).pack(fill=BOTH, padx=(5, 150), pady=(0, 10))

        Label(form, text="Bagages :", bg="LightSkyBlue1", anchor=W).pack(fill=BOTH, padx=15, pady=5)
        luggage_frame = Frame(form, bg="LightSkyBlue1")
        luggage_frame.pack(fill=BOTH, pady=(0, 10))
        Label(luggage_frame, text="Sac à dos", font=italic, bg="LightSkyBlue1", width=8).grid(row=1, column=1, padx=3)
        Label(luggage_frame, text="Sac à main", font=italic, bg="LightSkyBlue1", width=8).grid(row=1, column=2, padx=3)
        Label(luggage_frame, text="Valise", font=italic, bg="LightSkyBlue1", width=8).grid(row=1, column=3, padx=3)
        Label(luggage_frame, text="Encombrant", font=italic, bg="LightSkyBlue1", width=8).grid(row=1, column=4, padx=3)
        Spinbox(luggage_frame, from_=0, to=10, width=3, textvariable=self._backpack).grid(row=2, column=1)
        Spinbox(luggage_frame, from_=0, to=10, width=3, textvariable=self._handbag).grid(row=2, column=2)
        Spinbox(luggage_frame, from_=0, to=10, width=3, textvariable=self._suitcase).grid(row=2, column=3)
        Spinbox(luggage_frame, from_=0, to=10, width=3, textvariable=self._bulky).grid(row=2, column=4)

        Button(form, text="Calculer le meilleur itinéraire", font=bold, highlightbackground="LightSkyBlue1")\
            .pack(side=BOTTOM, pady=10)
        Button(form, text="Ajuster les préférences", highlightbackground="LightSkyBlue1").pack(side=LEFT, pady=(0, 15))
        Button(form, text="Sauvegarder le trajet", highlightbackground="LightSkyBlue1", command=self.save_ride)\
            .pack(side=RIGHT, pady=(0, 15))

        return form

    def save_ride(self):

        if not self._start.get() or not self._end.get():
            showwarning('Saisie incorrecte', "Vous devez renseigner l'adresse de départ et l'adresse d'arrivée")
            return
        departure_time = time.time() + 10 \
                         + 3600 * 24 * self._departure_minutes.get() \
                         + 3600 * self._departure_hours.get() \
                         + 60 * self._departure_minutes.get()
        result = self._system.new_ride(self._start.get(), self._end.get(), departure_time)
        if not result["success"]:
            showerror('Echec de configuration du trajet', result["error"])
            return

        luggage = dict()
        if self._backpack.get() > 0: luggage[BACKPACK] = self._backpack.get()
        if self._handbag.get() > 0: luggage[HANDBAG] = self._handbag.get()
        if self._suitcase.get() > 0: luggage[SUITCASE] = self._suitcase.get()
        if self._bulky.get() > 0: luggage[BULKY] = self._bulky.get()
        result = self._system.set_ride_precisions(self._travellers.get(), luggage)
        if not result["success"]:
            showerror('Paramêtrage incorrect', result["error"])
            return
        self.init_parameters()


if __name__ == "__main__":
    main_window = Tk()
    main_window.title("Comment y aller ?")
    system = HowToGoSystem()
    system.sign_up("LucieHmd", "enguerran", date(1994,07,04))
    page = RideSettingsPage(main_window, system)
    main_window.resizable(0, 0)
    main_window.mainloop()