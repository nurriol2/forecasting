#!/usr/bin/env python3

from exceptions import *
from item_ids import items

class TradeableItem:

    BASE_URL = "http://services.runescape.com/m=itemdb_oldschool"

    def __init__(self, name):

        self.name = name
        self.id = None
        self.GRAPH_ENDPOINT = None
        self.DETAILS_ENDPOINT = None 

        self._finish_initializing()

        return

    def _finish_initializing(self):
        self._set_id()
        if self.id==None:
            raise InvalidItemIDError
        else:
            self._format_DETAILS_ENDPOINT()
            self._format_GRAPH_ENDPOINT()
        return

    def _set_id(self):
        for item in items:
            if item["name"]==self.name.lower():
                self.id = item["id"]
        return

    def _format_DETAILS_ENDPOINT(self):
        self.DETAILS_ENDPOINT = "/api/catalogue/detail.json?item={}".format(self.id)
        return    

    def _format_GRAPH_ENDPOINT(self):

        self.GRAPH_ENDPOINT = "/api/graph/{}.json".format(self.id)

        return

    