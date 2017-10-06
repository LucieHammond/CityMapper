# -*- coding: utf-8 -*-

from api_manager import ApiManager


OPENDATA_API_URL = "https://opendata.paris.fr/api/records/1.0/search/"


class Stations(ApiManager):

    dataset = "default-dataset"

    def shape_url(self, rows=10, refine=None, sort=None):

        url = OPENDATA_API_URL + "?dataset=" + self.__class__.dataset
        if rows != 10:
            url += "&rows=" + str(rows)
        if refine:
            for facet, value in refine.items():
                url += "&refine." + facet + "=" + value
        if sort:
            url += "&sort=" + sort

        return url

    def find_data(self, point, is_start):
        raise NotImplementedError
