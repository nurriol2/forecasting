#!/usr/bin/env python3

import unittest
from tradeable_item import TradeableItem

class Test(unittest.TestCase):
    def test_collect_volume_time_series(self):

        dagger = TradeableItem("Rune Dagger")
        
        colnames = ["Close", "Average", "Volume"]

        for colname in colnames:
            assert dagger.table[colname].size == 179

        return
