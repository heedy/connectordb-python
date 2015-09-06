"""
This file is to perform manual testing of reconnection code.

Here's how:
    1) Start the file
    2) Shut down the connectordb server/disconnect from internet
    3) Make sure that reconnect attempts slow down
    4) Turn server back on
    5) Make sure that reconnect and resubscribe automatically happens
"""

import logging
logging.basicConfig(level=logging.DEBUG)

import connectordb

cdb = connectordb.ConnectorDB("test","test","localhost:8000")

s = cdb["reconnect_test"]

if not s.exists():
    s.create({"type":"string"})

def subscriber(stream,data):
    print stream,data

s.subscribe(subscriber)

import time
while True:
    time.sleep(100)
