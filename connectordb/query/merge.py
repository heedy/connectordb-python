from .._stream import Stream, query_maker


def get_stream(cdb, stream):
    if isinstance(stream, Stream):
        return stream.path
    elif stream.count("/") == 0:
        return cdb.path + "/" + stream
    elif stream.count("/") == 2:
        return stream
    else:
        raise Exception("Stream '%s' invalid" % (stream, ))


class Merge(object):
    """Merge represents a query which allows to merge multiple streams into one
    when reading, with all the streams merged together by increasing timestamp.
    The merge query is used as a constructor-type object::

        m = Merge(cdb)
        m.addStream("mystream1",t1=time.time()-10)
        m.addStream("mystream2",t1=time.time()-10)
        result = m.run()
    """

    def __init__(self, cdb):
        """Given a ConnectorDB object, begins the construction of a Merge query"""
        self.cdb = cdb

        self.query = []

    def addStream(self, stream, t1=None, t2=None, limit=None, i1=None, i2=None, transform=None):
        """Adds the given stream to the query construction. The function supports both stream
        names and Stream objects."""
        params = query_maker(t1, t2, limit, i1, i2, transform)

        params["stream"] = get_stream(self.cdb, stream)

        # Now add the stream to the query parameters
        self.query.append(params)

    def run(self):
        """Runs the merge query, and returns the result"""
        return self.cdb.db.query("merge", self.query)
