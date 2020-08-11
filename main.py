#!/usr/bin/env python3

from tradeable_item import TradeableItem
import matplotlib.pyplot as plt
import pandas as pd

def main():
    
    #red chinchompas item
    chins = TradeableItem("Red chinchompa")
    table = chins.table

    chins.plot_bar_graph("Item Timestamps", ["Volume"], "Volume of Units Moved per Day", ylabel="# of Red Chinchompas", save_plot=False)
    chins.plot_time_series("Item Timestamps", ["Close", "Average"], "Red Chins Closing and Average Price", ylabel="(GP)", save_plot=False, verbose=True)

    return

if __name__=="__main__":
    main()