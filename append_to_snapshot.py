#!/usr/bin/env python3

import pandas as pd
from tradeable_item import TradeableItem

def build_filename(item):
    """Format the item name to use as part of a CSV filename

    Args:
        item (str): The item to make a filename from

    Returns:
        (str): A formatted CSV filename
    """
    return item.strip(' ').lower().replace(' ', '_')+"_appended.csv"

def save_dataframe_here(item, data, data_dir="datasets/"):
    """Wrapper for pandas `DataFrame.to_csv()` that places `data` inside specified directory

    Args:
        item (str): The OSRS item
        data (pandas.DataFrame): A data frame combining the old snapshot and new data
        data_dir (str, optional): Directory to save the new CSV. Defaults to "datasets/".
    """

    filename = build_filename(item)
    fullpath = data_dir+filename
    data.to_csv(fullpath)
    print("Saving to {}".format(fullpath))
    return 

def append_new_data(item, old_snapshot, current, time_col="Timestamps_close"):
    """Combine the old snapshot with new data

    Args:
        old_snapshot (pandas.DataFrame): The old snapshot for an item
        current (pandas.DataFrame): The most up to date snapshot for an item
        time_col (str, optional): Name of the column to search for dates. Defaults to "Timestamps_close".
    """

    #get the lastest saved date in the old snapshot
    saved_date = old_snapshot[time_col].iloc[-1]

    #the index of the latest date as seen in the most up to date snapshot
    index = current[current[time_col]==saved_date].index.values[0]

    #the new data to append
    appendable = current.iloc[index:]

    #new dataframe with combined old and appendable data
    appended = old_snapshot.append(appendable, ignore_index=True, sort=False).drop(["Index"], axis=1)

    appended.to_csv(save_dataframe_here(item, appended))
    return 

def main(item, current_snapshot_path):
    
    #read in the lastest snapshot
    old_snapshot = pd.read_csv(current_snapshot_path)

    #get the most up to date snapshot
    current = TradeableItem(item).table
    
    append_new_data(item, old_snapshot, current)


    return 

if __name__ == "__main__":
    invested_items = {"Dragon Bones":"datasets/dragon_bones_04-10-2020.csv", 
                  "Black Dragonhide":"datasets/black_dragonhide_04-10-2020.csv", 
                  "Red Chinchompa":"datasets/red_chinchompa_04-10-2020.csv", 
                  "Black Chinchompa":"datasets/black_chinchompa_04-10-2020.csv", 
                  "Magic Logs":"datasets/magic_logs_04-10-2020.csv",
                  "Yew Longbow":"datasets/yew_longbow_04-10-2020.csv"}
    
    for item, path in invested_items.items():
        main(item, path)