import unittest

import connectordb
from connectordb.query import *

TEST_URL = "localhost:8000"


class TestQuery(unittest.TestCase):
    def setUp(self):
        self.db = connectordb.ConnectorDB("test", "test", url=TEST_URL)
        self.usr = self.db("query_test")
        if self.usr.exists():
            self.usr.delete()
        self.usr.create("loggertest@localhost", "mypass")
        self.device = self.usr["mydevice"]
        self.device.create()
        self.apikey = self.device.apikey
        self.udb = connectordb.ConnectorDB(self.apikey, url=TEST_URL)

    def tearDown(self):
        self.usr.delete()

    def test_merge(self):
        s1 = self.udb["stream1"]
        s2 = self.udb["stream2"]
        s3 = self.udb["stream3"]
        s1.create({"type": "number"})
        s2.create({"type": "number"})
        s3.create({"type": "number"})

        s1.insert_array([{"t": 1,
                          "d": 1}, {"t": 2,
                                    "d": 1}, {"t": 3,
                                              "d": 1}, {"t": 4,
                                                        "d": 1},
                         {"t": 5,
                          "d": 1}])
        s2.insert_array([{"t": 1.1,
                          "d": 2}, {"t": 2.1,
                                    "d": 2}, {"t": 3.1,
                                              "d": 2}, {"t": 4.1,
                                                        "d": 2},
                         {"t": 5.1,
                          "d": 2}])
        s3.insert_array([{"t": 1.2,
                          "d": 3}, {"t": 2.2,
                                    "d": 3}, {"t": 3.3,
                                              "d": 3}, {"t": 4.4,
                                                        "d": 3},
                         {"t": 5.5,
                          "d": 3}])

        m = Merge(self.udb)
        m.addStream(s1)
        m.addStream(s2.path, t1=3.0)
        m.addStream(s3.name, i1=1, i2=2)

        result = m.run()
        self.assertListEqual(result, [{"t": 1,
                                       "d": 1}, {"t": 2,
                                                 "d": 1}, {"t": 2.2,
                                                           "d": 3},
                                      {"t": 3,
                                       "d": 1}, {"t": 3.1,
                                                 "d": 2}, {"t": 4,
                                                           "d": 1},
                                      {"t": 4.1,
                                       "d": 2}, {"t": 5,
                                                 "d": 1}, {"t": 5.1,
                                                           "d": 2}])
