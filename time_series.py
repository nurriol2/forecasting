#!/usr/bin/env python3

import re
import pandas as pd
from datetime import datetime
from exceptions import TimestampError

class TimeSeries:

    def __init__(self, timestamps, signal):
        """Class wrapper for separating time series signals from timestamps.
        The mapping between timestamps and signal is assumed to be 1:1.

        Args:
            timestamps (list): The timestamps of the dataset. Agnostic to data type.
            signal (list): Signal being tracked via time series. Agnostic to data type.
        """
        self.timestamps = timestamps
        self.signal = signal
        
        self.timestamps = self._format_timestamps() 
        return 

    @classmethod
    def from_dictionary(self, data):
        """Create an instane of TimeSeries object from dictionary of data where
        the keys are the timestamps and the values are signal data points. 

        Args:
            data (dict): Time series data representation. 
            Keys are timestamps.
            Values are signal data points.

        Returns:
            TimeSeries: TimeSeries object representing `data`.
        """
        self.timestamps = list(data.keys())
        self.signal = list(data.values())
        return TimeSeries(self.timestamps, self.signal)

    def _format_timestamps(self):
        """Convert timestamps into datetime objects

        Raises:
            TimestampError: If timestamps do not match epoch or iso pattern

        Returns:
            list: list of timestamps as datetime objects
        """
        epoch_pattern = "\d{13}"
        iso_pattern = "\d{4}/\d{2}/\d{2}"

        formatted_timestamps = []
        if re.match(epoch_pattern, self.timestamps[0]):
            for ts in self.timestamps:
                fmt_ts = pd.to_datetime(int(ts), unit="ms").strftime("%Y/%m/%d")
                formatted_timestamps.append(fmt_ts)
        elif re.match(iso_pattern, self.timestamps[0]):
            for ts in self.timestamps:
                y, m, d = ts.split("/")
                fmt_ts = datetime(int(y), int(m), int(d)).strftime("%Y/%m/%d")
                formatted_timestamps.append(fmt_ts)
        else:
            raise TimestampError

        return formatted_timestamps
