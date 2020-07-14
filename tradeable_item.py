#!/usr/bin/env python3

import re
import requests
import pandas as pd
from item_ids import items 
from exceptions import InvalidItemIDError

class TradeableItem:

    BASE_URL = "http://services.runescape.com/m=itemdb_oldschool"

    def __init__(self, name, id=None, GRAPH_URL=None, VOLUME_URL=None, table=None):
        #IDEA:  Overriding the constructor might be better.
        #       However, with default arguments, the documentation is easier
        """Representation of an Old School Runescape (OSRS) Grand Exchange (GX) 
        listed item.

        Args:
            name (string): The name of the item, searchable on the GX
            id (int, optional): The ID representing the tradeable item in all OSRS GX API requests. Defaults to None.
            GRAPH_URL (string, optional): Redirects to webpage with a single JSON object for daily closing
                                          and daily average time series. Defaults to None.
            VOLUME_URL (string, optional): Redirects to the official OSRS GX page for TradeableItem. Defaults to None.
            table (pandas.DataFrame, optional): Concurrent, tabluar data of daily close, daily average, and trade volume for 
                                                last 6 months. Inexed on timestamps of daily close time series.. Defaults to None.
        """
        self.name = name.lower().strip("\n")
        self.id = id
        self.GRAPH_URL = GRAPH_URL
        self.VOLUME_URL = VOLUME_URL
        self.table = table

        self._finish_initializing() 
        
        return

    def _search_id_by_name(self):
        """Use the tradeable item's name to search a file on disk for its ID

        Raises:
            InvalidItemIDError: If searching the file leaves the `candidate_id==None`.

        Returns:
            int: The ID used to identify a tradeable item in all OSRS GX API requests
        """
        candidate_id = None
        for item in items:
            if item["name"]==self.name:
                candidate_id = item["id"]
        if candidate_id==None:
            raise InvalidItemIDError
        return candidate_id
    
    def _initialize_item_id(self):
        """Set the value for the tradeable item ID

        Returns:
            int: The ID used to identify a tradeable item in all OSRS GX API requests
        """
        return self._search_id_by_name()

    def _finish_initializing(self):
        """Set the values for all class attributes in specified order.
        For information on TradeableItems attributes, see constructor.
        """
        self.id = self._initialize_item_id()
        self.GRAPH_URL = self.BASE_URL + "/api/graph/{}.json".format(self.id)
        self.VOLUME_URL = self.BASE_URL + "/{}/viewitem?obj={}".format(self.name.replace(' ', "+"), self.id)
        self.table = self._initialize_table() 
        return

    #web scraping
    def _collect_price_time_series(self):
        """Parse the requested JSON for daily close time series data 
        and daily average time series data.

        Returns:
            tuple: Ordered pair of dictionaries containing time series data
            for both the daily close time series and daily average time series.
            Keys are strings representing ms since epoch.
            Values are integers representing the signal (amount of gp)
        """
        r = requests.get(self.GRAPH_URL)
        #dictionary of 2 dictionaries, "daily" and "average"
        response = r.json()
        daily_series, average_series = (response["daily"], response["average"])
        return (daily_series, average_series)

    def _collect_volume_time_series(self):
        """Parse the OSRS GX tradeable item webpage for trade volume data.

        Returns:
            dict: Single dictionary containing trade volume time series data.
            Keys are strings in `%Y-%m-%d` format.
            Values are integers representing the number of unites moved by close.
        """
        #fetch the item page as text
        page_as_text = requests.get(self.VOLUME_URL).text
        
        #search the item page for tags that contain volume information
        volume_tags = re.findall("trade180.push.*", page_as_text)

        volume_series = {}
        #iterate over all the tags just found
        for match in volume_tags:
            tv_pairs = re.findall("Date\(.*\), \d+", match)
            #separate the timestamps from volume data
            for pair in tv_pairs:
                t, v = tuple(pair.split(','))
                #remove text surrounding Y/M/D piece of timestamp
                t = t.strip("Date('").strip("')'")
                volume_series[t] = v
        return volume_series

    def _initialize_table(self):
        """Populate the `table` attribute with daily close, daily average, and
        trade volume data for the last 6 months. 
        The table is indexed on timestamps of each data point.

        Returns:
            pandas.DataFrame: A 180x3 DataFrame.
            Columns:  Close, Average, Volume
            Index: Timestamps as pandas datetime objects
        """
        close_series, average_series = self._collect_price_time_series()
        volume_series = self._collect_volume_time_series()

        #each series is concurrent
        #so, the timestamps from the daily close series represents all timestamps
        timestamp = pd.to_datetime(list(close_series.keys()), unit="ms")

        #dump the signal data into lists
        volume = list(volume_series.values())
        close = list(close_series.values())
        average = list(average_series.values())

        #PROBLEM:   (checked at 14/6/20 00:49) Volume time series size is mismatching Close and Average. 
        #           However, wrote test on 13/06/20 to explicitly check that the size was 180 and
        #           all the tests passed, then.
        data = {"Close":close, "Average":average, "Volume":volume} 
        #index the DataFrame by ms since epoch
        df = pd.DataFrame(data=data, index=timestamp)
        
        return df
