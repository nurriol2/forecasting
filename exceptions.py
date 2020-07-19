#!/usr/bin/env python3

class InvalidItemIDError(Exception):
    """Raised when `name` is not found in `item_ids.py`
    """

    def __init__(self, message="The entered name did not yield a valid item ID. Item id:  None"):
        self.message = message
        super().__init__(self.message)

class MismatchedSeriesSizeError(Exception):
    """Raised if series is initialized with time series of different lengths
    """
    def __init__(self, expected_npts, candidate, seriesID):
        self.expected_npts = expected_npts
        self.candidate = candidate
        self.seriesID = seriesID
        self.message = "One or more columns has a different size than expected.\nExpecting {} entries.\nGot {} entries in series {}.".format(self.expected_npts, self.candidate, self.seriesID)
        super().__init__(self.message)