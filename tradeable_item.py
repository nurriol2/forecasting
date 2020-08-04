#!/usr/bin/env python3

import re
import requests
import pandas as pd
from datetime import date
from item_ids import items 
from time_series import TimeSeries
from exceptions import InvalidItemIDError, MismatchedSeriesSizeError

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
        daily_series = TimeSeries.from_dictionary(response["daily"])
        average_series = TimeSeries.from_dictionary(response["average"])
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
                volume_series[t] = int(v)
        volume_series = TimeSeries.from_dictionary(volume_series)
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
        #TODO:  clean up series conversions
        close_series, average_series = self._collect_price_time_series()
        volume_series = self._collect_volume_time_series()

        vdf = volume_series.to_pandas_dataframe("Volume")
        cdf = close_series.to_pandas_dataframe("Close")
        adf = average_series.to_pandas_dataframe("Average")
        #outer join close and average
        price_df = cdf.join(adf, on=None, how='left', lsuffix="_close", rsuffix="_average")
        
        df = price_df.merge(vdf, how="outer", left_on=price_df["Timestamps_close"], right_on=vdf["Timestamps"], validate="one_to_one").dropna()
        return df



    def save_table_to_file(self):
        """Download the current state of `table` as a csv file in the current directory.
        """
        
        #format the filename
        current_date = date.today().strftime("%d-%m-%Y")
        filename = self.name.replace(' ', "_") + '_' + current_date + ".txt"
        
        self.table.to_csv(filename, index_label="Index")

        return
