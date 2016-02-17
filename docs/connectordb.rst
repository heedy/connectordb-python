===================
Core API Reference
===================

This page is the direct API reference.

The User, Device, and Stream objects all inherit from ConnectorObject, meaning that all methods and properties in ConnectorObject can be accessed from any other object in the core API.

The ConnectorDB object is the API main entrance point, and it inherits from Device. When logging in to ConnectorDB, you are logging in as a device, and all operations are done in reference to that device::

    import connectordb
    cdb = connectordb.ConnectorDB("apikey")
    #Prints the full username/devicename path of the logged in device
    print cdb.path

This is something you must be aware of when logging in as a user. Using a password actually logs you in as the user device, and all operations are done in reference to this device.
Therefore, when logging in as a user, you will need to do the following::

    import connectordb
    cdb = connectordb.ConnectorDB("username","password")
    # cdb is now the username/user device
    myuser = cdb.user
    # myuser is the "username" user, which can list devices
    print myuser.devices()


ConnectorObject
++++++++++++++++

.. automodule:: connectordb._connectorobject
    :members:
    :undoc-members:
    :show-inheritance:

ConnectorDB
++++++++++++++++

.. automodule:: connectordb._connectordb
    :members:
    :undoc-members:
    :show-inheritance:

User
++++++++++++++++
.. automodule:: connectordb._user
    :members:
    :undoc-members:
    :show-inheritance:

Device
++++++++++++++++

.. automodule:: connectordb._device
    :members:
    :undoc-members:
    :show-inheritance:

Stream
++++++++++++++++
.. automodule:: connectordb._stream
    :members:
    :undoc-members:
    :special-members:
    :show-inheritance:
