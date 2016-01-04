from __future__ import absolute_import

import unittest
import time
import os

import connectordb
from connectordb.logger import Logger, DATAPOINT_INSERT_LIMIT

TEST_URL = "localhost:8000"


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.db = connectordb.ConnectorDB("test", "test", url=TEST_URL)
        self.usr = self.db("logger_test")
        if self.usr.exists():
            self.usr.delete()
        self.usr.create("loggertest@localhost", "mypass")
        self.device = self.usr["mydevice"]
        self.device.create()
        self.apikey = self.device.apikey

        if os.path.exists("test.db"):
            os.remove("test.db")

    def tearDown(self):
        try:
            self.usr.delete()
        except:
            pass

    def test_inserting(self):
        s = self.device["mystream"]

        def test_create(l):
            l.apikey = self.apikey
            l.serverurl = TEST_URL
            l.data = "Hello World!!!"
            l.syncperiod = 3.3

            l.addStream("mystream", {"type": "string"})

            haderror = False
            try:
                l.addStream("stream_DNE")
            except:
                haderror = True

            self.assertTrue(haderror)

        self.assertFalse(s.exists())
        l = Logger("test.db", on_create=test_create)
        self.assertTrue(s.exists())

        self.assertEqual("logger_test/mydevice", l.name)
        self.assertEqual(self.apikey, l.apikey)
        self.assertEqual(TEST_URL, l.serverurl)

        self.assertEqual(0, len(l))

        self.assertTrue("mystream" in l)
        self.assertFalse("stream_DNE" in l)

        l.insert("mystream", "Hello World!")

        self.assertEqual(1, len(l))
        self.assertEqual("Hello World!!!", l.data)

        l.close()

        def nocreate(self):
            raise Exception("OnCreate was called on existing database!")

        # Now reload from file and make sure everything was saved
        l = Logger("test.db", on_create=nocreate)
        self.assertEqual(1, len(l))
        self.assertEqual(l.name, "logger_test/mydevice")
        self.assertTrue("mystream" in l)
        self.assertTrue(self.apikey, l.apikey)
        self.assertTrue(TEST_URL, l.serverurl)
        self.assertTrue(3.3, l.syncperiod)

        haderror = False
        try:
            l.insert(5)  # Make sure that the schema is checked correctly
        except:
            haderror = True
        self.assertTrue(haderror)

        l.insert("mystream", "hi")

        self.assertEqual(2, len(l))
        self.assertEqual(0, len(s))
        l.sync()
        self.assertEqual(0, len(l))
        self.assertEqual(2, len(s))

        self.assertGreater(l.lastsynctime, time.time() - 1)

        self.assertEqual("Hello World!!!", l.data)

        self.assertEqual(s[0]["d"], "Hello World!")
        self.assertEqual(s[1]["d"], "hi")
        self.assertGreater(s[1]["t"], time.time() - 1)

        l.close()

    def test_bgsync(self):
        s = self.device["mystream"]

        # This time we test existing stream
        s.create({"type": "string"})

        l = Logger("test.db")
        l.serverurl = TEST_URL
        l.apikey = self.apikey

        l.addStream("mystream")

        l.syncperiod = 1

        self.assertEqual(0, len(s))
        self.assertEqual(0, len(l))

        l.start()
        l.insert("mystream", "hi")
        l.insert("mystream", "hello")
        self.assertEqual(0, len(s))
        self.assertEqual(2, len(l))
        time.sleep(1.1)
        self.assertEqual(2, len(s))
        self.assertEqual(0, len(l))
        l.insert("mystream", "har")
        self.assertEqual(2, len(s))
        self.assertEqual(1, len(l))
        time.sleep(1.1)
        self.assertEqual(3, len(s))
        self.assertEqual(0, len(l))
        l.stop()

        l.insert("mystream", "stopped")
        time.sleep(1.3)
        self.assertEqual(3, len(s))
        self.assertEqual(1, len(l))

        l.close()

    def test_overflow(self):
        global DATAPOINT_INSERT_LIMIT
        dil = DATAPOINT_INSERT_LIMIT
        DATAPOINT_INSERT_LIMIT = 2
        s = self.device["mystream"]

        # This time we test existing stream
        s.create({"type": "string"})

        l = Logger("test.db")
        l.serverurl = TEST_URL
        l.apikey = self.apikey

        l.addStream("mystream")

        l.insert("mystream","test1")
        l.insert("mystream","test2")
        l.insert("mystream","test3")

        l.sync()

        self.assertEqual(3, len(s))
        self.assertEqual(0, len(l))

        DATAPOINT_INSERT_LIMIT = dil

if __name__ == "__main__":
    unittest.main()
