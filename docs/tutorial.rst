===================
Tutorial
===================

This page is the tutorial for ConnectorDB's python interface.


Installing
+++++++++++++

To start using ConnectorDB, you need to install it!::
    
    pip install connectordb
    
If you don't have pip installed, you can `follow these instructions <https://pip.pypa.io/en/stable/installing/>`_.

You will also want to install apsw::

    sudo apt-get install python-apsw
    
If on Windows, you can get the binaries from `here <http://www.lfd.uci.edu/~gohlke/pythonlibs/#apsw>`_. APSW is used for logging support.

Connecting
++++++++++++++

Once installed, you can log in as a user::

    import connectordb
    cdb = connectordb.ConnectorDB("username","password",url="https://cdb.mysite.com")
    
...and as a device::

    import connectordb
    cdb = connectordb.ConnectorDB("apikey",url="https://cdb.mysite.com")
    
After logging in, you can check your device by looking at the path:

    >>> cdb.path
    'myuser/user'

Basics
++++++++++++++

Let's check what streams we have:

    >>> cdb.streams()
    [[Stream:myuser/user/productivity], [Stream:myuser/user/mood]]

Since you're logged in as a device, you see your streams.
You can access this device's streams directly by name::

    >>> productivity = cdb["productivity"]
    >>> productivity
    [Stream:myuser/user/productivity]
    
Let's see some of the stream's properties:

    >>> productivity.schema
    {'type': 'integer', 'maximum': 10, 'minimum': 0}
    >>> productivity.datatype
    'rating.stars'
    >>> productivity.description
    ''
    
This is a star-rating stream. This stream should have a description, though - let's set it!

    >>> productivity.description = "A star rating of my productivity"
    >>> productivity.description
    'A star rating of my productivity'
    
You can also see all of the stream's properties and set them:

    >>> productivity.data
    {'name': 'productivity', 'ephemeral': False, 'datatype': 'rating.stars', 'description': 'A star rating of my productivity', 'downlink': False, 'schema': '{"type":"integer","minimum":0,"maximum":10}', 'icon': '', 'nickname': ''}
    >>> productivity.set({"nickname": "My Productivity"})
    
The same methods of access work for users and devices as well.

Stream Data
+++++++++++++++

Let's do some basic analysis of the productivity stream::

    >>> len(productivity)
    9

Looks like I only have 9 productivity ratings in my stream. All of the data in streams
is accessible like a python array. The first element of the array is the oldest datapoint. ConnectorDB's streams are append-only, so you don't need to worry about data disappearing/appearing in the middle of the array.

Let's get the most recent productivity rating

    >>> productivity[-1]
    {'t': 1464334185.668, 'd': 8}
    
Looks like I was really productive recently (8/10 stars)! When exactly was this timestamp?

    >>> from datetime import datetime
    >>> datetime.fromtimestamp(productivity[-1]["t"])
    'Fri May 27 03:29:45 2016'

Let's perform analysis of the whole stream. We can get the full stream's data by getting productivity[:]

    >>> productivity[:]
    [{'t': 1464250199.934, 'd': 8}, {'t': 1464334179.605, 'd': 7}, {'t': 1464334180.216, 'd': 5}, {'t': 1464334180.88, 'd': 9}, {'t': 1464334181.782, 'd': 3}, {'t': 1464334183.308, 'd': 1}, {'t': 1464334183.752, 'd': 5}, {'t': 1464334184.46, 'd': 4}, {'t': 1464334185.668, 'd': 8}]

For our current analysis, we don't need the timestamps:
    
    >>> list(map(lambda x: x["d"],productivity[:]))
    [8, 7, 5, 9, 3, 1, 5, 4, 8]
    
Let's find the mean:

    >>> import statistics
    >>> statistics.mean(map(lambda x: x["d"],productivity[:]))
    5.555555555555555
    
If we only care about the mean, it is inefficient to query the entire dataset from ConnectorDB, only to perform an aggregation that returns a single value. We can use PipeScript to perform
the aggregation on the server:

    >>> productivity(transform="mean | if last")
    [{'t': 1464334185.668, 'd': 5.555555555555555}]

You can `go here for a PipeScript tutorial <https://connectordb.github.io/pipescript/>`_ (PipeScript is ConnectorDB's transform engine)

Using the call syntax, you can also query ConnectorDB by time. To get the datapoints from the last minute:

    >>> productivity(t1=time.time() -60, t2=time.time())
    
Finally, let's plot the rating vs time:
    
    >>> from pylab import *
    >>> t,d = zip(*map(lambda x: (datetime.fromtimestamp(x["t"]),x["d"]),productivity[:]))
    >>> plot(t,d)
    >>> show()

Subscribing
++++++++++++++

Suppose now that you want to do something whenever your mood is greater than 8 stars.
To do this, you need to somehow be notified when this happens. ConnectorDB allows devices
to subscribe to streams, so that you get data the moment it is inserted:

    >>> def subscriber(stream,data):
    ...     print(stream,data)
    >>> productivity.subscribe(subscriber)
    
Now go to the ConnectorDB web app, and change your productivity rating. You should see your new data be printed the moment you click on the rating.

But we only want to get datapoints where productivity is greater than 8! Let's unsubscribe.

    >>> productivity.unsubscribe()
    
ConnectorDB's subscriptions accept transforms, so we filter the datapoints with rating 8 or lower.

    >>> productivity.subscribe(subscriber,transform="if $>8")
    
Now you should only get messages when the rating is greater than 8 stars!

Subscribing allows your devices to react to your data. Before continuing, let's unsubscribe:

    >>> productivity.unsubscribe(transform="if $>8")
    
The transform string used during unsubscribing must be exactly the same as the one used when subscribing, because you can have multiple subscriptions each with different transforms.

Devices
+++++++++

We know how to view data in ConnectorDB - let's figure out how to create it in the first place.

We will go back to the cdb device we logged in with. Let's make a new stream:

    >>> newstream = cdb["newstream"]
    >>> newstream.exists()
    False
    
This stream doesn't exist yet, so make it:

    >>> newstream.create({"type":"string"})

Let's add data!

    >>> len(newstream)
    0
    >>> newstream.insert("Hello World!")
    >>> len(newstream)
    1
    
Note that we are currently logged in as the user device. This is not recommended. ConnectorDB
is built with the assumption that every physical program/object using it has its own associated device, using which it accesses the database. Therefore, let's create
a new device for ourselves.

We must first go to the user to list devices

    >>> cdb.user.devices()
    [[Device:test/user], [Device:test/meta]]
    
ConnectorDB comes with two devices by default, the user and meta device. The meta device is hidden in the web interface, as it holds log streams. The user device represents the user.

    >>> newdevice = cdb.user["newdevice"]
    >>> newdevice.exists()
    False
    >>> newdevice.create()
    
    
Now let's log in as that device:

    >>> newdevice.apikey
    '4d79a2c0-3a02-45da-7131-9f5f3d6e4696'
    >>> mydevice = connectordb.ConnectorDB(newdevice.apikey,url="https://cdb.mysite.com")
    
You'll notice that this device is completely isolated - it does not have access to anything but itself and its own streams. This is because the default role given to devices assumes that they are not to be trusted with data. 

.. warning::
    ConnectorDB's permissions structure is there to disallow snooping - and not active malice.
    Each device can create an arbitrary amount of streams and is not rate limited by default.
    
Downlinks
+++++++++++

One of the powerful features of ConnectorDB are downlinks. First let's see an unusual property of
devices:

    >>> mys = mydevice["mystream"]
    >>> mys.create({"type": "number"})

    >>> s = newdevice["mystream"]
    
Notice that both s and mys refer to the same stream. The difference between the two is that s is logged in as a user, and has access to everything, and mys is logged in as the device which owns mystream.

    >>> mys.insert(54)
    >>> s.insert(12)
    connectordb._connection.AuthenticationError: '403: Write access to stream data denied. (529afdba-9cdc-48ae-4fbb-0e8adf6d3ed9)'
    
What happened here? Shouldn't s be able to write the stream? 

ConnectorDB is set up such that only
the owning device can write its streams. This is to enforce isolation. Each device should only write to its own streams.

.. note::
    All permissions can be modified to suit your liking in connectordb's configuration files.
    This behavior is in the default configuration.

There is one major case where this behavior would be suboptimal. Suppose you want to control your
lights through ConnectorDB. Your lights create a stream which gives the current on/off state, and want other devices to be able to turn the lights on and off.

This is what the downlink property of a stream is for
    
    >>> mys.downlink = True

Now you can insert the data!

    >>> len(s)
    >>> 2
    >>> s.insert(3)
    >>> len(s)
    >>> 2
    
...It looks like the insert succeeded, but the data wasn't inserted!? 

ConnectorDB's downlinks
do not actually permit you to insert data directly to the stream - the stream reflects reality,
and your lights are currently off. The intervention (turn lights on/set thermostat to 75F) is placed into a special downlink stream
    
    >>> s.length(downlink=True)
    1
    >>> s(downlink=True)
    [{'t': 1464350691.0983202, 'd': 3, 'o': 'test/user'}]
    
The downlink stream says that the device 'test/user' wants the value to be 3. Now it is the owning device's (lights) job to set the actual stream value correctly.

This would usually be done by subscribing to the downlink stream

    >>> def lightcontrol(streamname,data):
    ...     print("The lights are now",data[-1]["d"])
    ...     return data
    >>> mys.subscribe(lightcontrol,downlink=True)

By returning True from the light control callback, or returning the data, we're acknowledging that we set the value - and the stream value is accepted. We can also return an arbitrary datapoint to set a different value, or return False, or nothing at all, which will not acknowledge the datapoint. This is useful when there is a time delay between setting goal value and actual value (such as when controlling a thermostat).

Now, when we set values, they are inserted to the stream after being acknowledged by the device:

    >>> len(s)
    2
    >>> s.insert(9)
    >>> len(s)
    3


And that's it!

You now know enough to begin using ConnectorDB. There are two major components which were not touched upon in this tutorial: logging and datasets.

The python interface includes special logging code which allows you to easily write logging devices which periodically synchronize data with ConnectorDB. If gathering data from sensors, you probably want to use the logger.

Datasets are in the queries section - they enable you to perform computation by combining multiple streams into one tabular structure which is easy to plug into machine learning and statistical packages. If doing advanced analysis, you'll want to look at datasets.

