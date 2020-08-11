#!/usr/bin/env python3

import math
import pandas as pd
import matplotlib.pyplot as plt
from tradeable_item import TradeableItem
from sklearn.preprocessing import MinMaxScaler

def main():
    
    #red chinchompas item
    chins = TradeableItem("Red chinchompa")
    table = chins.table

    #chins.plot_bar_graph("Item Timestamps", ["Volume"], "Vol. of Red Chins Moved per Day", ylabel="# of Red Chins Sold", save_plot=False, verbose=True)
    #chins.plot_time_series("Item Timestamps", ["Close", "Average"], "Red Chins Closing and Average Price", ylabel="Price (GP)", save_plot=False, verbose=True)
    #chins.correlation_matrix(["Close", "Average", "Volume"], " Red Chins Correlation Matrix", save=False, verbose=True)
    
    #add normalized data to the table
    cols = ["Close", "Average", "Volume"]
    for c in cols:
        scaler = MinMaxScaler()
        data = table[c].to_numpy().reshape(-1,1)
        norm_data = scaler.fit_transform(data).flatten()
        table["Normalized {}".format(c)] = norm_data
    
    return

if __name__=="__main__":
    main()