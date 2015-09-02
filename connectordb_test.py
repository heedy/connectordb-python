import unittest
import time
import connectordb

from jsonschema import SchemaError

TEST_URL = "localhost:8000"


class TestConnectorDB(unittest.TestCase):
    def setUp(self):
        self.db = connectordb.ConnectorDB("test", "test", url=TEST_URL)
        self.usr = self.db("python_test")
        if self.usr.exists():
            self.usr.delete()
        self.usr.create("pythontest@localhost", "mypass")
        self.usrdb = connectordb.ConnectorDB("python_test",
                                             "mypass",
                                             url=TEST_URL)

    def tearDown(self):
        self.usrdb.close()
        try:
            self.usr.delete()
        except:
            pass
        self.db.close()

    def test_authfail(self):
        try:
            connectordb.ConnectorDB("notauser", "badpass", url=TEST_URL)
        except connectordb.AuthenticationError:
            return

    def test_basics(self):
        self.assertEqual(self.db.path, "test/user")
        self.assertEqual(self.db.name, "user")
        self.assertEqual(self.db.user.name, "test")
        i = self.db.info()
        self.assertTrue(len(i["version"]) > 1)
        self.assertTrue(len(i["interpolators"]) > 1)
        self.assertTrue(len(i["transforms"]) > 1)

    def test_counting(self):
        db = self.db
        self.assertGreaterEqual(db.count_users(), 1)
        self.assertGreaterEqual(db.count_devices(), 1)
        self.assertGreaterEqual(db.count_streams(), 1)

        usr = db("python_counting_test")
        if usr.exists():
            usr.delete()
        self.assertFalse(usr.exists())
        curusers = db.count_users()
        usr.create("test@email.com", "mypass")
        curusers += 1
        self.assertEqual(curusers, db.count_users())

        self.assertRaises(connectordb.AuthenticationError,
                          self.usrdb.count_streams)
        self.assertRaises(connectordb.AuthenticationError,
                          self.usrdb.count_devices)
        self.assertRaises(connectordb.AuthenticationError,
                          self.usrdb.count_streams)

        curdevices = db.count_devices()
        curstreams = db.count_streams()

        self.usrdb["counting_stream"].create({"type": "string"})
        curstreams += 1

        self.assertEqual(curusers, db.count_users())
        self.assertEqual(curdevices, db.count_devices())
        self.assertEqual(curstreams, db.count_streams())

        self.usrdb.user["countdevice"].create()
        curdevices += 1

        self.assertEqual(curusers, db.count_users())
        self.assertEqual(curdevices, db.count_devices())
        self.assertEqual(curstreams, db.count_streams())

    def test_user(self):
        self.assertEqual(self.db.user.exists(), True)
        self.assertEqual(self.db(self.usrdb.user.name).exists(), True)
        self.assertEqual(self.usrdb.exists(), True)
        self.assertEqual(self.db("baduser").exists(), False)
        self.assertEqual(self.usrdb("test").exists(), False)

        self.assertEqual("admin" in self.db.data, True)
        self.assertEqual("admin" in self.usrdb.data, False)

        self.assertEqual(self.usrdb.user.name, "python_test")
        self.usrdb.user.email = "testemail@change"
        self.assertEqual(self.usrdb.user.email, "testemail@change")

        self.usrdb.user.set_password("newpass")
        usrdb = connectordb.ConnectorDB("python_test", "newpass", url=TEST_URL)
        self.assertEqual(usrdb.path, "python_test/user")

        self.usr.set({"admin": True})

        usrdb.refresh()
        self.assertEqual("admin" in usrdb.data, True)

        usrdb.user.nickname = "myuser"
        self.assertEqual(self.db("python_test").nickname, "myuser")

        self.assertRaises(connectordb.AuthenticationError, self.usr.set,
                          {"admin": "Hello"})

    def test_device(self):
        db = self.usrdb
        self.assertEqual(len(db.user.devices()), 2)
        self.assertFalse(db.user["mydevice"].exists())
        db.user["mydevice"].create()
        self.assertTrue(db.user["mydevice"].exists())
        self.assertEqual(3, len(db.user.devices()))

        dev = connectordb.ConnectorDB(db.user["mydevice"].apikey, url=TEST_URL)
        self.assertEqual(1, len(dev.user.devices()))  # Device has no access to other devices

        dev.nickname = "test nickname"
        self.assertEqual(db("python_test/mydevice").nickname, "test nickname")

        apikey = dev.apikey
        newkey = dev.reset_apikey()
        self.assertRaises(connectordb.AuthenticationError, dev.refresh)
        self.assertFalse(apikey == newkey)
        dev = connectordb.ConnectorDB(newkey, url=TEST_URL)
        self.assertEqual(dev.nickname, "test nickname")

        self.assertEqual(dev.user.name, "python_test")

    def test_stream(self):
        self.assertRaises(SchemaError, self.usrdb["mystream"].create,
                          {"type": "blah blah"})
        initialstreams = len(self.usrdb.streams())
        s = self.usrdb["mystream"]
        self.assertFalse(s.exists())
        s.create({"type": "string"})
        self.assertTrue(s.exists())
        self.assertEqual(len(self.usrdb.streams()), initialstreams + 1)

        self.assertEqual(s.user.name, "python_test")
        self.assertEqual(s.device.name, "user")

        self.assertEqual(s.ephemeral, False)
        self.assertEqual(s.downlink, False)
        s.ephemeral = True
        self.assertEqual(s.ephemeral, True)
        self.assertEqual(s.downlink, False)
        s.downlink = True
        self.assertEqual(s.ephemeral, True)
        self.assertEqual(s.downlink, True)

        s.delete()
        self.assertFalse(s.exists())

    def test_streamio(self):
        s = self.usrdb("python_test/user/mystream")

        s.create({"type": "string"})
        self.assertEqual(0, len(s))

        s.insert("Hello World!")
        self.assertEqual(1, len(s))

        self.assertEqual("Hello World!", s[0]["d"])
        self.assertEqual("Hello World!", s(0)[0]["d"])

        s.ephemeral = True

        s.insert("another hello!")
        s.insert("yet another hello!")

        self.assertEqual(1, len(s))

        s.ephemeral = False

        s.insert("1")
        time.sleep(0.1)
        s.insert_array([{"d": "2", "t": time.time() - 0.01}, {"d": "3"}])

        self.assertEqual("3", s[-1]["d"])
        self.assertEqual(3, len(s[1:]))
        self.assertEqual(4, len(s[:]))

        self.assertEqual(s.schema["type"], "string")

    def test_struct(self):
        # This test is specifically to make sure that structs are correctly sent back (this was a bug in connectordb)
        s = self.usrdb["mystream"]

        s.create({
            "type": "object",
            "properties": {
                "test": {"type": "string"},
                "t2": {"type": "number"}
            }
        })

        s.insert({"test": "hi!", "t2": -1337.1})

        v = s[-1]["d"]
        self.assertEqual(v["test"], "hi!")
        self.assertEqual(v["t2"], -1337.1)

    def test_call(self):
        s = self.usrdb["teststream"]
        s.create({"type": "number"})

        s.insert_array([{"d": 3}, {"d": 10}, {"d": 4}, {"d": 35}, {"d": 9}])

        dp = s(i1=0, i2=0, transform="if $>5 | $<20")
        self.assertEqual(3, len(dp))
        self.assertEqual(True, dp[0]["d"])
        self.assertEqual(False, dp[1]["d"])
        self.assertEqual(True, dp[2]["d"])
