===================
Queries
===================

ConnectorDB includes special queries optimized for generating datasets from the time series data associated
with streams. There are 2 main query types:

merge
	Puts together multiple streams into one combined stream

dataset
	Takes multiple streams and uses their time series to generate
	tabular data ready for use in plotting and ML applications.


Merge
++++++++++++++++

.. automodule:: connectordb.query.merge
    :members:
    :undoc-members:
    :show-inheritance:

Dataset
++++++++++++++++

.. automodule:: connectordb.query.dataset
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members:
