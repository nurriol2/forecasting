#!/usr/bin/env python3

#TODO:  clean up series conversions
#TODO:  experiment with different line widths for *SAVED* bar graphs
#TODO:  condense bar and line plotting

import re
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
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

    ### WEB SCRAPING ###
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

    ### PREPROCESSING ###
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

        vdf = volume_series.to_pandas_dataframe("Volume")
        cdf = close_series.to_pandas_dataframe("Close")
        adf = average_series.to_pandas_dataframe("Average")
        
        #outer join close and average
        price_df = cdf.join(adf, on=None, how="outer", lsuffix="_close", rsuffix="_average")
        
        df = price_df.merge(vdf, how="outer", left_on=price_df["Timestamps_close"], right_on=vdf["Timestamps"], validate="one_to_one").dropna()
        df = df.rename(columns={"key_0":"Item Timestamps"})
        return df

    ### PLOTTING ###
    def plot_bar_graph(self, index, signal, title, ylabel="", steps=25, save_plot=True, verbose=False):
        """Create a bar plot. Pandas + Matplotlib plotting wrapper that automatically handles x-axis formatting for 
        better looking labels.

        Args:
            index (string): The name of the column holding the x-axis data.
            signal (list): A list of strings for each column name with y-data.
            title (string): Title for the plot.
            ylabel (string, optional): Label for the y-axis. Defaults to "".
            steps (int, optional): Spacing between x-axis labels. Defaults to 25.
            save_plot (bool, optional): Flag for if the plot should be saved. Defaults to True.
            verbose (bool, optional): Flag for if the plot should be displayed. Defaults to False.
        """

        #grab the x-axis data
        data = {index:self.table[index]}
        #grab the y-axis data
        for i in signal:
            data[i] = self.table[i]
        df = pd.DataFrame(data=data)
        ax = df.plot.bar(x=index, title=title, rot=35)
        
        #x-axis tick marks formatting
        ticks = ax.xaxis.get_ticklocs()
        ticklabels = [l.get_text() for l in ax.xaxis.get_ticklabels()]
        #set tick marks at intervals of `steps` using the record value in the index column
        ax.xaxis.set_ticks(ticks[::steps])
        ax.xaxis.set_ticklabels(ticklabels[::steps])

        #axis labels
        ax.set(xlabel="Date", ylabel=ylabel)

        
        if save_plot:
            filename = title.lower().replace(' ', '_') + "_bar_plot.png"
            plt.savefig(filename)
        if verbose:
            plt.show()
        return 

    def plot_time_series(self, index, signal, title, ylabel="", save_plot=True, verbose=False):
        """Create a line plot. Pandas + Matplotlib plotting wrapper.

        Args:
            index (string): The name of the column holding the x-axis data.
            signal (list): A list of strings for each column name with y-data.
            title (string): Title for the plot.
            ylabel (string, optional): Label for the y-axis. Defaults to "".
            save_plot (bool, optional): Flag for if the plot should be saved. Defaults to True.
            verbose (bool, optional): Flag for if the plot should be displayed. Defaults to False.
        """
        data = {index:self.table[index]}
        #grab the y-axis data
        for i in signal:
            data[i] = self.table[i]
        df = pd.DataFrame(data=data)
        ax = df.plot(x=index, title=title, rot=35)

        #axis labels
        ax.set(xlabel="Date", ylabel=ylabel)

        if save_plot:
            filename = title.lower().replace(' ', '_') + "_bar_plot.png"
            plt.savefig(filename)
        if verbose:
            plt.show()
        return

    ### FILES OUT ###
    def save_table_to_file(self):
        """Download the current state of `table` as a csv file in the current directory.
        """
        
        #format the filename
        current_date = date.today().strftime("%d-%m-%Y")
        filename = self.name.replace(' ', '_') + '_' + current_date + ".csv"
        
        self.table.to_csv(filename, index_label="Index")
        return

    
