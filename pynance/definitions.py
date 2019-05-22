"""
This module contains common definitions that are shared across other pynance
modules.
"""

import numpy as np

IMMUTABLE_COLUMNS = {
    "date": np.datetime64,
    "sender_account": str,
    "receiver_account": str,
    "text": str,
    "amount": np.float64,
    "total_balance": np.float64,
    "currency": str,
    "origin": str
}

# see issue #5 and #6
# use numpy types for numbers, because that's what pandas likes
COLUMNS = dict(id=str,
               category=str,
               tags=str, **IMMUTABLE_COLUMNS)
