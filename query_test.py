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

    def test_tdataset(self):
        s1 = self.udb["temperature"]

        s1.create({"type": "number"})

        s1.insert_array([{"t": 2,
                          "d": 73}, {"t": 5,
                                     "d": 84}, {"t": 8,
                                                "d": 81}, {"t": 11,
                                                           "d": 79}])

        ds = Dataset(self.udb, t1=0, t2=8, dt=2)

        ds.addStream("temperature", "closest")

        res = ds.run()

        self.assertEqual(5, len(res))
        self.assertListEqual(
            res, [{
                "d": {"temperature": {"t": 2,
                                      "d": 73}}
            }, {"t": 2,
                "d": {"temperature": {"t": 2,
                                      "d": 73}
                      }}, {"t": 4,
                           "d": {"temperature": {"t": 5,
                                                 "d": 84}}},
                  {"t": 6,
                   "d": {"temperature": {"t": 5,
                                         "d": 84}
                         }}, {"t": 8,
                              "d": {"temperature": {"t": 8,
                                                    "d": 81}}}])

    def test_ydataset(self):
        s1 = self.udb["temperature"]
        s2 = self.udb["mood_rating"]

        s1.create({"type": "number"})
        s2.create({"type": "number"})

        s1.insert_array([{"t": 2,
                          "d": 73}, {"t": 5,
                                     "d": 84}, {"t": 8,
                                                "d": 81}, {"t": 11,
                                                           "d": 79}])
        s2.insert_array([{"t": 1,
                          "d": 7}, {"t": 4,
                                    "d": 3}, {"t": 11,
                                              "d": 5}])

        ds = Dataset(self.udb, s2)
        ds.addStream("temperature", "closest")
        res = ds.run()

        self.assertListEqual(res, [
            {
                "t": 1,
                "d": {"temperature": {"t": 2,
                                      "d": 73},
                      "y": {"t": 1,
                            "d": 7}}
            }, {
                "t": 4,
                "d": {"temperature": {"t": 5,
                                      "d": 84},
                      "y": {"t": 4,
                            "d": 3}}
            }, {
                "t": 11,
                "d":
                {"temperature": {"t": 11,
                                 "d": 79},
                 "y": {"t": 11,
                       "d": 5}}
            }
        ])
