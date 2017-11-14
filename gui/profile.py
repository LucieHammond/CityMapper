# -*- coding: utf-8 -*-

from Tkinter import *
from tkMessageBox import *
from constants import VELIB_NO_SUBSCRIPTION, VELIB_TICKETS_30M, VELIB_SUBSCRIPTION_30M, VELIB_SUBSCRIPTION_45M,\
    AUTOLIB_PRET_A_ROULER, AUTOLIB_FIRST_RENTING_OFFER, AUTOLIB_PREMIUM,\
    SUBWAY_NAVIGO_SUBSCRIPTION, SUBWAY_TICKETS_BOOK, SUBWAY_TICKETS_REDUCED, SUBWAY_NO_TITLE,\
    FASTEST, LESS_WALKING, CHEAPEST, WEATHER_IMPACT, LESS_PAINFUL, SIMPLEST, SHORTEST, OSX

VELIB_SUBSCRIPTIONS = {VELIB_SUBSCRIPTION_30M: u"Abonnement Vélib' Classique (30 min offertes)",
                       VELIB_SUBSCRIPTION_45M: u"Abonnement Vélib' Passion ou Vélib' Solidarité (45 min offertes)",
                       VELIB_TICKETS_30M: u"Tickets courte durée '1 jour' ou '7 jours' (30 min offertes)",
                       VELIB_NO_SUBSCRIPTION: u"Aucun titre Vélib pour le moment"}

AUTOLIB_SUBSCRIPTIONS = {AUTOLIB_PREMIUM: u"Abonnement Autolib' Premium (tarif location préférentiel)",
                         AUTOLIB_PRET_A_ROULER: u"Abonnement Autolib' Prêt A Rouler (gratuit, tarif par défault)",
                         AUTOLIB_FIRST_RENTING_OFFER: u"Offre '1ère location offerte' à utiliser avec Prêt A Rouler"}

SUBWAY_SUBSCRIPTIONS = {SUBWAY_NAVIGO_SUBSCRIPTION: u"Forfait illimité (Navigo, ImagineR, Mobilis, Visite, Week End..)",
                        SUBWAY_TICKETS_BOOK: u"Tickets T+ par carnets de 10",
                        SUBWAY_TICKETS_REDUCED: u"Tickets T+ par carnets de 10 (tarif réduit)",
                        SUBWAY_NO_TITLE: u"Aucun titre de transport RATP (ou ticket T+ à l'unité)"}


class ProfilePage(Frame):
    """ Page de modification du profil utilisateur (avec 2 volets : informations et préférences) """

    def __init__(self, window, system, page=1):
        Frame.__init__(self, window, width=1000, height=600, bg="burlywood1")
        self.pack()
        self.pack_propagate(0)
        self._window = window
        self._system = system

        # Titres de transports / Permis de conduire
        self._velib = StringVar()
        self._velib.set(VELIB_SUBSCRIPTIONS[system.current_user.subscriptions["velib"]])
        self._autolib = StringVar()
        self._autolib.set(AUTOLIB_SUBSCRIPTIONS[system.current_user.subscriptions["autolib"]])
        self._subway = StringVar()
        self._subway.set(SUBWAY_SUBSCRIPTIONS[system.current_user.subscriptions["subway"]])
        self._driving_licence = BooleanVar()
        self._driving_licence.set(system.current_user.driving_licence)

        # Préférences
        self._fastest = IntVar()
        self._fastest.set(system.current_user.preferences[FASTEST])
        self._less_walking = IntVar()
        self._less_walking.set(system.current_user.preferences[LESS_WALKING])
        self._cheapest = IntVar()
        self._cheapest.set(system.current_user.preferences[CHEAPEST])
        self._weather_impact = IntVar()
        self._weather_impact.set(system.current_user.preferences[WEATHER_IMPACT])
        self._less_painful = IntVar()
        self._less_painful.set(system.current_user.preferences[LESS_PAINFUL])
        self._simplest = IntVar()
        self._simplest.set(system.current_user.preferences[SIMPLEST])
        self._shortest = IntVar()
        self._shortest.set(system.current_user.preferences[SHORTEST])

        self.frame = self.subscriptions_form() if page == 1 else self.preferences_form()
        self.frame.pack(fill=BOTH, expand=YES, padx=30, pady=30)
        self.frame.pack_propagate(0)

    def page_1(self):
        """ Affiche la page 1 du profil """
        self.frame.pack_forget()
        self.frame = self.subscriptions_form()
        self.frame.pack(fill=BOTH, expand=YES, padx=30, pady=30)
        self.frame.pack_propagate(0)

    def page_2(self):
        """ Affiche la page 2 du profil """
        self.frame.pack_forget()
        self.frame = self.preferences_form()
        self.frame.pack(fill=BOTH, expand=YES, padx=30, pady=30)
        self.frame.pack_propagate(0)

    def subscriptions_form(self):
        """ Crée et renvoie le formulaire sur les infos de transport (page 1) """
        form = LabelFrame(self, text="Gestion du profil utilisateur (page 1)", width=940, height=540, bg="ghost white")
        h1 = ("Helvetica", 16, "bold") if OSX else ("Helvetica", 15, "bold")
        h2 = ("Lucida", 14, "bold") if OSX else ("Calibri", 12, "bold")

        # Titres de transport
        frame1 = Frame(form, width=450, height=470, bg="ghost white")
        frame1.grid(row=1, column=1, padx=(20, 0))
        frame1.pack_propagate(0)
        Label(frame1, text="1. Titres de transport", font=h1, bg="ghost white", anchor=W).pack(pady=20, fill=BOTH)
        Label(frame1, text="De quels forfaits ou abonnements disposez vous pour les moyens\nde transports suivants ?",
              bg="ghost white", anchor=W, justify=LEFT).pack(pady=(0, 10), fill=BOTH)

        # - Forfaits Vélib
        Label(frame1, text="Vélib", bg="ghost white", font=h2, anchor=W).pack(pady=(10, 0), padx=(10, 0), fill=BOTH)
        velib_options = OptionMenu(frame1, self._velib, *VELIB_SUBSCRIPTIONS.values())
        velib_options.config(width=50)
        velib_options.pack(padx=(0, 20))

        # - Forfaits Autolib
        Label(frame1, text="Autolib", bg="ghost white", font=h2, anchor=W).pack(pady=(15, 0), padx=(10, 0), fill=BOTH)
        autolib_options = OptionMenu(frame1, self._autolib, *AUTOLIB_SUBSCRIPTIONS.values())
        autolib_options.config(width=50)
        autolib_options.pack(padx=(0, 20))

        # - Forfaits RATP
        Label(frame1, text="Transports en commun", bg="ghost white", font=h2, anchor=W).pack(pady=(15, 0), padx=(10, 0), fill=BOTH)
        autolib_options = OptionMenu(frame1, self._subway, *SUBWAY_SUBSCRIPTIONS.values())
        autolib_options.config(width=50)
        autolib_options.pack(padx=(0, 20))

        # Permis de conduire
        frame2 = Frame(form, width=450, height=470, bg="ghost white")
        frame2.grid(row=1, column=2, padx=(0, 20))
        frame2.pack_propagate(0)
        Label(frame2, text="2. Permis de conduire", font=h1, bg="ghost white", anchor=W).pack(pady=20, fill=BOTH)
        Checkbutton(frame2, text=" Je suis en posséssion d'un permis de conduire valide", bg="ghost white", anchor=W,
                    variable=self._driving_licence, justify=LEFT).pack(pady=(0, 10), fill=BOTH)

        # Informations globales
        Label(frame2, text="3. Informations générales", font=h1, bg="ghost white", anchor=W)\
            .pack(pady=(50, 20), fill=BOTH)
        username = " - Nom d'utilisateur : " + self._system.current_user.username
        birthdate = " - Date de naissance : %s (%d ans)" % (self._system.current_user.birthdate,
                                                            self._system.current_user.age)
        Label(frame2, text=username, bg="ghost white", anchor=W).pack(pady=(0, 5), fill=BOTH)
        Label(frame2, text=birthdate, bg="ghost white", anchor=W).pack(pady=(0, 5), fill=BOTH)

        # Navigation
        Button(form, text="<< Précédent", width=13, state=DISABLED).grid(row=2, column=1, pady=5, padx=(0, 250))
        Button(form, text="Terminer", width=13, command=self.save_changes).grid(row=2, column=2, pady=5, padx=(0, 100))
        Button(form, text="Suivant >>", width=13, command=self.page_2).grid(row=2, column=2, pady=5, padx=(250, 0))
        return form

    def preferences_form(self):
        """ Crée et renvoie le formulaire sur les préférences utilisateur (page 2) """
        form = LabelFrame(self, text="Gestion du profil utilisateur (page 2)", width=940, height=540, bg="ghost white")
        h1 = ("Helvetica", 16, "bold") if OSX else ("Helvetica", 15, "bold")
        italic = ("Lucida", 14, "italic") if OSX else ("Calibri", 10, "italic")

        frame = Frame(form, width=900, height=470, bg="ghost white")
        frame.grid(row=1, column=1, columnspan=2, padx=20)
        frame.pack_propagate(0)
        Label(frame, text="4. Préférences d'optimisation pour les trajets", font=h1,
              bg="ghost white", anchor=W).pack(pady=20, fill=BOTH)
        Label(frame, text="Quelle importance accordez-vous aux critères d'optimisation suivants ?",
              bg="ghost white", anchor=W, justify=LEFT).pack(pady=(0, 10), fill=BOTH)

        table = Frame(frame, bg="ghost white")
        table.pack()

        # Première ligne : degrés d'importance
        Label(table, text="Critères :", bg="ghost white", width=24, anchor=W).grid(row=1, column=1)
        Label(table, text="Importance\nmaximale", bg="ghost white", width=12, font=italic).grid(row=1, column=2)
        Label(table, text="Très\nimportant", bg="ghost white", width=12, font=italic).grid(row=1, column=3)
        Label(table, text="Vraiment\nimportant", bg="ghost white", width=12, font=italic).grid(row=1, column=4)
        Label(table, text="Moyennement\nimportant", bg="ghost white", width=12, font=italic).grid(row=1, column=5)
        Label(table, text="Pas très\nimportant", bg="ghost white", width=12, font=italic).grid(row=1, column=6)
        Label(table, text="Aucune\nimportance", bg="ghost white", width=12, font=italic).grid(row=1, column=7)

        # Première colonne : critères
        Label(table, text="- Le plus rapide", bg="ghost white", anchor=W, width=24)\
            .grid(row=2, column=1, pady=(15, 0))
        Label(table, text="- Le moins de marche à pied", bg="ghost white", anchor=W, width=24)\
            .grid(row=3, column=1, pady=(15, 0))
        Label(table, text="- Le moins cher", bg="ghost white", anchor=W, width=24)\
            .grid(row=4, column=1, pady=(15, 0))
        Label(table, text="- Le plus adapté à la météo", bg="ghost white", anchor=W, width=24)\
            .grid(row=5, column=1, pady=(15, 0))
        Label(table, text="- Le moins pénible*", bg="ghost white", anchor=W, width=24)\
            .grid(row=6, column=1, pady=(15, 0))
        Label(table, text="- Le moins de changements", bg="ghost white", anchor=W, width=24)\
            .grid(row=7, column=1, pady=(15, 0))
        Label(table, text="- Le plus direct (distance)", bg="ghost white", anchor=W, width=24)\
            .grid(row=8, column=1, pady=(15, 0))

        # Plus rapide
        Radiobutton(table, variable=self._fastest, value=5, bg="ghost white").grid(row=2, column=2, pady=(13, 0))
        Radiobutton(table, variable=self._fastest, value=4, bg="ghost white").grid(row=2, column=3, pady=(13, 0))
        Radiobutton(table, variable=self._fastest, value=3, bg="ghost white").grid(row=2, column=4, pady=(13, 0))
        Radiobutton(table, variable=self._fastest, value=2, bg="ghost white").grid(row=2, column=5, pady=(13, 0))
        Radiobutton(table, variable=self._fastest, value=1, bg="ghost white").grid(row=2, column=6, pady=(13, 0))
        Radiobutton(table, variable=self._fastest, value=0, bg="ghost white").grid(row=2, column=7, pady=(13, 0))

        # Moins de marche
        Radiobutton(table, variable=self._less_walking, value=5, bg="ghost white").grid(row=3, column=2, pady=(13, 0))
        Radiobutton(table, variable=self._less_walking, value=4, bg="ghost white").grid(row=3, column=3, pady=(13, 0))
        Radiobutton(table, variable=self._less_walking, value=3, bg="ghost white").grid(row=3, column=4, pady=(13, 0))
        Radiobutton(table, variable=self._less_walking, value=2, bg="ghost white").grid(row=3, column=5, pady=(13, 0))
        Radiobutton(table, variable=self._less_walking, value=1, bg="ghost white").grid(row=3, column=6, pady=(13, 0))
        Radiobutton(table, variable=self._less_walking, value=0, bg="ghost white").grid(row=3, column=7, pady=(13, 0))

        # Moins cher
        Radiobutton(table, variable=self._cheapest, value=5, bg="ghost white").grid(row=4, column=2, pady=(13, 0))
        Radiobutton(table, variable=self._cheapest, value=4, bg="ghost white").grid(row=4, column=3, pady=(13, 0))
        Radiobutton(table, variable=self._cheapest, value=3, bg="ghost white").grid(row=4, column=4, pady=(13, 0))
        Radiobutton(table, variable=self._cheapest, value=2, bg="ghost white").grid(row=4, column=5, pady=(13, 0))
        Radiobutton(table, variable=self._cheapest, value=1, bg="ghost white").grid(row=4, column=6, pady=(13, 0))
        Radiobutton(table, variable=self._cheapest, value=0, bg="ghost white").grid(row=4, column=7, pady=(13, 0))

        # Impact météorologique
        Radiobutton(table, variable=self._weather_impact, value=5, bg="ghost white").grid(row=5, column=2, pady=(13, 0))
        Radiobutton(table, variable=self._weather_impact, value=4, bg="ghost white").grid(row=5, column=3, pady=(13, 0))
        Radiobutton(table, variable=self._weather_impact, value=3, bg="ghost white").grid(row=5, column=4, pady=(13, 0))
        Radiobutton(table, variable=self._weather_impact, value=2, bg="ghost white").grid(row=5, column=5, pady=(13, 0))
        Radiobutton(table, variable=self._weather_impact, value=1, bg="ghost white").grid(row=5, column=6, pady=(13, 0))
        Radiobutton(table, variable=self._weather_impact, value=0, bg="ghost white").grid(row=5, column=7, pady=(13, 0))

        # Moins pénible compte tenu de la charge
        Radiobutton(table, variable=self._less_painful, value=5, bg="ghost white").grid(row=6, column=2, pady=(13, 0))
        Radiobutton(table, variable=self._less_painful, value=4, bg="ghost white").grid(row=6, column=3, pady=(13, 0))
        Radiobutton(table, variable=self._less_painful, value=3, bg="ghost white").grid(row=6, column=4, pady=(13, 0))
        Radiobutton(table, variable=self._less_painful, value=2, bg="ghost white").grid(row=6, column=5, pady=(13, 0))
        Radiobutton(table, variable=self._less_painful, value=1, bg="ghost white").grid(row=6, column=6, pady=(13, 0))
        Radiobutton(table, variable=self._less_painful, value=0, bg="ghost white").grid(row=6, column=7, pady=(13, 0))

        # Moins de changements
        Radiobutton(table, variable=self._simplest, value=5, bg="ghost white").grid(row=7, column=2, pady=(13, 0))
        Radiobutton(table, variable=self._simplest, value=4, bg="ghost white").grid(row=7, column=3, pady=(13, 0))
        Radiobutton(table, variable=self._simplest, value=3, bg="ghost white").grid(row=7, column=4, pady=(13, 0))
        Radiobutton(table, variable=self._simplest, value=2, bg="ghost white").grid(row=7, column=5, pady=(13, 0))
        Radiobutton(table, variable=self._simplest, value=1, bg="ghost white").grid(row=7, column=6, pady=(13, 0))
        Radiobutton(table, variable=self._simplest, value=0, bg="ghost white").grid(row=7, column=7, pady=(13, 0))

        # Plus court
        Radiobutton(table, variable=self._shortest, value=5, bg="ghost white").grid(row=8, column=2, pady=(13, 0))
        Radiobutton(table, variable=self._shortest, value=4, bg="ghost white").grid(row=8, column=3, pady=(13, 0))
        Radiobutton(table, variable=self._shortest, value=3, bg="ghost white").grid(row=8, column=4, pady=(13, 0))
        Radiobutton(table, variable=self._shortest, value=2, bg="ghost white").grid(row=8, column=5, pady=(13, 0))
        Radiobutton(table, variable=self._shortest, value=1, bg="ghost white").grid(row=8, column=6, pady=(13, 0))
        Radiobutton(table, variable=self._shortest, value=0, bg="ghost white").grid(row=8, column=7, pady=(13, 0))

        Label(frame, text="* compte tenu des bagages à transporter", font=italic, bg="ghost white", anchor=W)\
            .pack(padx=10, pady=10, fill=BOTH)

        # Navigation
        Button(form, text="<< Précédent", width=13, command=self.page_1).grid(row=2, column=1, pady=5, padx=(0, 250))
        Button(form, text="Terminer", width=13, command=self.save_changes).grid(row=2, column=2, pady=5, padx=(0, 100))
        Button(form, text="Suivant >>", width=13, state=DISABLED).grid(row=2, column=2, pady=5, padx=(250, 0))
        return form

    def save_changes(self):
        """ Enregistre les changements du profil utilisateur et redirige vers la page principale de la plateforme """

        velib, autolib, subway = None, None, None
        for key, value in VELIB_SUBSCRIPTIONS.iteritems():
            if self._velib.get() == value:
                velib = key
                break
        for key, value in AUTOLIB_SUBSCRIPTIONS.iteritems():
            if self._autolib.get() == value:
                autolib = key
                break
        for key, value in SUBWAY_SUBSCRIPTIONS.iteritems():
            if self._subway.get() == value:
                subway = key
                break
        preferences = {
            FASTEST: self._fastest.get(),
            SHORTEST: self._shortest.get(),
            CHEAPEST: self._cheapest.get(),
            SIMPLEST: self._simplest.get(),
            WEATHER_IMPACT: self._weather_impact.get(),
            LESS_PAINFUL: self._less_painful.get(),
            LESS_WALKING: self._less_walking.get()
        }

        result = self._system.set_profile_settings(velib, autolib, subway, self._driving_licence.get(), preferences)
        if not result["success"]:
            showerror('Erreur système', result["error"])
            return

        # Redirection vers la page principale
        from settings import RideSettingsPage
        self.pack_forget()
        RideSettingsPage(self._window, self._system)
