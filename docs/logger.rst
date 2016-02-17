===================
Logging Data
===================

Sometimes you just want to gather data at all times, and sync to ConnectorDB periodically.
The logger allows you to do exactly such a thing.

The logger caches datapoints to a local sqlite database, and synchronizes with ConnectorDB
every 10 minutes by default.

Suppose you have a temperature sensor on a computer with an intermittent internet connection.

You can use the Logger to cache data until a sync can happen::

	def getTemperature():
	    #Your code here
	    pass

	from connectordb.logger import Logger

	def initlogger(l):
	    # This function is called when first creating the Logger, to initialize the values

	    # api key is needed to get access to ConnectorDB
	    l.apikey = raw_input("apikey:")

	    # If given a schema (as we have done here), addStream will create the stream if it doesn't exist
	    l.addStream("temperature",{"type":"number"})

	    # Sync with ConnectorDB once an hour (in seconds)
	    l.syncperiod = 60*60

	# Open the logger using a cache file name (where datapoints are cached before syncing)
	l = Logger("cache.db", on_create=initlogger)

	# Start running syncer in background (can manually run l.sync() instead)
	l.start()

	# While the syncer is running in the background, we are free to add data
	# to the cache however we want - it will be saved first to the cache file
	# so that you don't lose any data, and will be synced to the database once an hour
	while True:
	    time.sleep(60)
	    l.insert("temperature",getTemperature())

The logger requires the python-apsw package to work. It is a thread-safe sqlite wrapper, which is used
to safely store your data between synchronization attempts.

On ubuntu, you can run ``apt-get install python-apsw``. On windows, you will need to download the extension package from http://www.lfd.uci.edu/~gohlke/pythonlibs/#apsw , and install
using pip.

Logger
++++++++++++++++

.. automodule:: connectordb.logger
    :members:
    :undoc-members:
    :show-inheritance:
