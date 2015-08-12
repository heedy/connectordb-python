===================
Core API Reference
===================

This page is the direct API reference.

The User, Device, and Stream objects all inherit from ConnectorObject, meaning that all methods and properties in ConnectorObject can be accessed from any other object in the core API.

The ConnectorDB object is the API main entrance point, and it inherits from Device. That's right, when logging in to ConnectorDB, you are logging in as a device, and all operations are done in reference to that device::

    import connectordb
    cdb = connectordb.ConnectorDB("apikey")
    #Prints the full username/devicename path of the logged in device
    print cdb.path

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
    
