# -*- coding: utf-8 -*-

class User():

    total_users = 0

    def __init__(self, username, password, age):
        User.total_users += 1
        self._id = User.total_users
        self._username = username
        self._password = password
        self._age = age

    def set_subscriptions_infos(self, velib, autolib, subway):
        self._subscriptions = {"velib": velib, "autolib": autolib, "subway": subway}

    def set_preferences(self):
        pass