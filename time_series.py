#!/usr/bin/env python3

import re
import pandas as pd

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

    def _format_timestamps(self, timestamps):
        epoch_pattern = "\d{13}"
        
        return 
