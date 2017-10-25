# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
from core.system import HowToGoSystem
from datetime import date
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
        self._departure_hours = IntVar()
        self._departure_minutes = IntVar()
        self._departure_seconds = IntVar()
        self._travellers = IntVar()
        self._backpack = IntVar()
        self._handbag = IntVar()
        self._suitcase = IntVar()
        self._bulky = IntVar()
        self._map = None

        self.config_menu()

    def config_menu(self):

        # Le menubar de tkinter ne fonctionne pas sur Mac. Je simule donc un menu à la main
        menubar = Frame(self, height=30, bg="SlateGray3", relief=RAISED, borderwidth=2)
        menubar.pack(fill=BOTH)
        Label(menubar, text="%s :" % self._system.current_user.username, font=(None, 14, "bold"), bg="SlateGray3")\
            .pack(side=LEFT, padx=(10,5))
        Button(menubar, text="Mon profil", highlightbackground="SlateGray3", command=self.display_profile_1)\
            .pack(side=LEFT, padx=5)
        Button(menubar, text="Mes préférences", highlightbackground="SlateGray3", command=self.display_profile_2)\
            .pack(side=LEFT, padx=5)
        Button(menubar, text="Deconnexion", highlightbackground="SlateGray3", command=self.deconnection)\
            .pack(side=RIGHT, padx=5)
        self._window.config(menu=menubar)

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
        self.pack_forget()
        HomePage(self._window, self._system)


if __name__ == "__main__":
    main_window = Tk()
    main_window.title("Comment y aller ?")
    system = HowToGoSystem()
    system.sign_up("LucieHmd", "enguerran", date(1994,07,04))
    page = RideSettingsPage(main_window, system)
    main_window.resizable(0, 0)
    main_window.mainloop()