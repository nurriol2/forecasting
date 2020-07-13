#!/usr/bin/env python3

import re
import requests
import pandas as pd
from item_ids import items 
from exceptions import InvalidItemIDError

class TradeableItem:

    BASE_URL = "http://services.runescape.com/m=itemdb_oldschool"

    def __init__(self, name):
        self.name = name.lower().strip("\n")
        self.id = self._initialize_item_id()
        self.GRAPH_URL = self.BASE_URL + "/api/graph/{}.json".format(self.id)
        self.VOLUME_URL = self.BASE_URL + "/{}/viewitem?obj={}".format(self.name.replace(' ', "+"), self.id)
        self.table = self._initialize_table()
        
        return

    def _search_id_by_name(self):
        candidate_id = None
        for item in items:
            if item["name"]==self.name:
                candidate_id = item["id"]
        if candidate_id==None:
            raise InvalidItemIDError
        return candidate_id
    
    def _initialize_item_id(self):
        return self._search_id_by_name()

    #web scraping
    def _collect_price_time_series(self):
        r = requests.get(self.GRAPH_URL)
        response = r.json()
        daily_series, average_series = (response["daily"], response["average"])
        return (daily_series, average_series)

    def _collect_volume_time_series(self):
        #fetch the item page as text
        page_as_text = requests.get(self.VOLUME_URL).text
        
        #search for tags with volume data
        volume_tags = re.findall("trade180.push.*", page_as_text)

        volume_series = {}
        for match in volume_tags:
            tv_pairs = re.findall("Date\(.*\), \d+", match)
            for pair in tv_pairs:
                t, v = tuple(pair.split(','))
                #remove text surrounding Y/M/D piecce of timestamp
                t = t.strip("Date('").strip("')'")
                volume_series[t] = v
        return volume_series
    


    def _initialize_table(self):
        close_series, average_series = self._collect_price_time_series()
        volume_series = self._collect_volume_time_series()

        timestamp = pd.to_datetime(list(close_series.keys()), unit="ms")
        volume = list(volume_series.values())
        close = list(close_series.values())
        average = list(average_series.values())

        data = {"Close":close, "Average":average, "Volume":volume}
        df = pd.DataFrame(data=data, index=timestamp)
        
        return df
