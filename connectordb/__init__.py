"""The official python client for ConnectorDB.

The client enables quick usage of the database for IoT stuff and data analysis::

    import time
    import connectordb

    cdb = connectordb.ConnectorDB("apikey")

    temp = cdb["temperature"]

    if not temp.exists():
        temp.create({"type": "number"})

    while True:
        time.sleep(1)
        t = get_temperature()
        temp.insert(t)

"""
from __future__ import absolute_import

from ._connectordb import *
from ._connection import AuthenticationError, ServerError

__version__ = "0.3.0a3"
