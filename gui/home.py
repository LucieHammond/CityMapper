# -*- coding: utf-8 -*-

from core.system import HowToGoSystem
from Tkinter import *
from tkMessageBox import *
from datetime import date
import re


class HomePage(Frame):

    def __init__(self, window, system):
        Frame.__init__(self, window, width=1000, height=600, bg="DarkSeaGreen1")
        self.pack()
        self.pack_propagate(0)
        self._window = window
        self._system = system

        self._image = None
        self._username = StringVar()
        self._password = StringVar()
        self._birthdate = StringVar()

        self.frame = self.home_frame()
        self.frame.pack(padx=30, pady=30)
        self.frame.pack_propagate(0)

    def home_frame(self):
        frame = Frame(self, width=940, height=540, bg="DarkSeaGreen2", relief=SUNKEN, borderwidth=2)
        image_panel = Canvas(frame, width=900, height=425, bg="DarkSeaGreen2", highlightthickness=0)
        self._image = PhotoImage(file="../resources/logo.gif")
        image_panel.create_image(0, 0, anchor=NW, image=self._image)
        image_panel.pack(side=TOP, padx=20)
        sign_up = Button(frame, text="Inscription", width=20, highlightbackground="DarkSeaGreen2",
                         command=self.start_registration)
        sign_up.pack(side=LEFT, padx=125)
        sign_in = Button(frame, text="Connection", width=20, highlightbackground="DarkSeaGreen2",
                         command=self.start_connection)
        sign_in.pack(side=RIGHT, padx=125)
        return frame

    def connection_form(self):
        form = LabelFrame(self, text="Connection", width=400, height=400, bg="ghost white")

        username_label = Label(form, text="Nom d'utilisateur :", bg="ghost white")
        username_label.pack(pady=(40, 0))
        username_entry = Entry(form, textvariable=self._username, width=30)
        username_entry.pack()

        password_label = Label(form, text="Mot de passe :", bg="ghost white")
        password_label.pack(pady=(30, 0))
        password_entry = Entry(form, textvariable=self._password, width=30, show="*")
        password_entry.pack()

        sign_up = Button(form, text="Inscription", width=15, command=self.start_registration)
        sign_up.pack(side=BOTTOM, pady=(0, 25))
        infos = Label(form, text="Vous n'avez pas encore de compte ?\n"
                                 "Inscrivez vous gratuitement en cliquant ici", bg="ghost white")
        infos.pack(side=BOTTOM, pady=(0, 5))

        back = Button(form, text="Retour", width=9, command=self.get_back)
        back.pack(side=LEFT, padx=(60, 0))
        throw = Button(form, text="SE CONNECTER", width=13, command=self.sign_in)
        throw.pack(side=RIGHT, padx=(0, 60))

        return form

    def registration_form(self):
        form = LabelFrame(self, text="Inscription", width=400, height=400, bg="ghost white")

        username_label = Label(form, text="Nom d'utilisateur :", bg="ghost white")
        username_label.pack(pady=(40, 0))
        username_entry = Entry(form, textvariable=self._username, width=30)
        username_entry.pack()

        password_label = Label(form, text="Mot de passe :", bg="ghost white")
        password_label.pack(pady=(30, 0))
        password_entry = Entry(form, textvariable=self._password, width=30, show="*")
        password_entry.pack()

        birthdate_label = Label(form, text="Date de naissance (jj/mm/aaaa):", bg="ghost white")
        birthdate_label.pack(pady=(30, 0))
        birthdate_entry = Entry(form, textvariable=self._birthdate, width=30)
        birthdate_entry.pack()

        back = Button(form, text="Retour", width=9, command=self.get_back)
        back.pack(side=LEFT, padx=(60, 0))
        throw = Button(form, text="S'INSCRIRE", width=13, command=self.sign_up)
        throw.pack(side=RIGHT, padx=(0, 60))

        return form

    def start_connection(self):
        self.frame.pack_forget()
        self.frame = self.connection_form()
        self.frame.pack(fill=BOTH, expand=YES, padx=300, pady=100)
        self.frame.pack_propagate(0)

    def start_registration(self):
        self.frame.pack_forget()
        self.frame = self.registration_form()
        self.frame.pack(fill=BOTH, expand=YES, padx=300, pady=100)
        self.frame.pack_propagate(0)

    def get_back(self):
        self.frame.pack_forget()
        self.frame = self.home_frame()
        self.frame.pack(padx=30, pady=30)
        self.frame.pack_propagate(0)

    def sign_up(self):
        # Vérifie le format des données et transforme la date string en date datetime
        if not self._username.get() or not self._password.get() or not self._birthdate.get():
            showwarning('Saisie incorrecte', "Vous devez renseigner tous les champs demandés")
            return
        regex = re.match("^(\d{2})/(\d{2})/(\d{4})$", self._birthdate.get())
        if not regex:
            showwarning('Saisie incorrecte', "Votre date de naissance doit être au format jj/mm/aaaa\n"
                                             "Par exemple 04/07/1994...")
            return
        day = int(regex.group(1))
        month = int(regex.group(2))
        year = int(regex.group(3))
        try:
            birthdate = date(year, month, day)
        except ValueError:
            showwarning('Saisie incorrecte', "La date de naissance indiquée ne correspond à aucune date valide")
            return
        else:
            result = self._system.sign_up(self._username.get(), self._password.get(), birthdate)
            if not result["success"]:
                showwarning('Erreur système', result["error"])
                return

        from profile import ProfilePage
        self.pack_forget()
        ProfilePage(self._window, self._system)

    def sign_in(self):
        # Vérifie le format des données
        if not self._username.get() or not self._password.get():
            showwarning('Saisie incorrecte', "Vous devez renseigner tous les champs demandés")
            return
        result = self._system.sign_in(self._username.get(), self._password.get())
        if not result["success"]:
            showwarning('Erreur système', result["error"])
            return

        from settings import RideSettingsPage
        self.pack_forget()
        RideSettingsPage(self._window, self._system)


if __name__ == "__main__":
    main_window = Tk()
    main_window.title("Comment y aller ?")
    system = HowToGoSystem()
    home_page = HomePage(main_window, system)
    main_window.resizable(0, 0)
    main_window.mainloop()
