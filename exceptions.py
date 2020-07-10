#!/usr/bin/env python3

class InvalidItemIDError(Exception):
    """Raised when `TradeableItem.name` is not found in `items`.

    Args:
        Error (InvalidItemID): When a `TradeableItem` is created, a `name` variable is set. Then, `name` 
        is used to search a list of dictionaries mapping the item id to the item name. If the search yields
        no result, `TradeableItem.id` == `None`.
    """

    def __init__(self, message="The entered name did not yield a valid item ID. Item id:  None"):
        self.message = message
        super().__init__(self.message)