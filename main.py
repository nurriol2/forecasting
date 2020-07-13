#!/usr/bin/env python3

from tradeable_item import TradeableItem

def main():

    magicLogs = TradeableItem("Magic Logs")
    t = magicLogs.table
    print(t.head())
    print(t.shape)
    return

if __name__=="__main__":
    main()