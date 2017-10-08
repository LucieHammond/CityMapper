# -*- coding: utf-8 -*-

class User():

    total_users = 0

    def __init__(self, username, password):
        self._username = username
        self._password = password