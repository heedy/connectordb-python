from __future__ import absolute_import

import unittest

from connectordb import DatapointArray


class TestDatapointArray(unittest.TestCase):

    def test_basics(self):
        d= DatapointArray([{"t": 2345,"d": 45},{"t": 2348,"d": 8}])

        self.assertEqual(2,len(d))
        self.assertEqual(d[0]["d"],45)
        self.assertEqual(d[1]["d"],8)

        self.assertEqual(len(d["d"]),2)
        self.assertEqual(len(d["t"]),2)
        self.assertEqual(d["d"][1],8)

    def test_extras(self):
        d= DatapointArray([{"t": 2345,"d": 45},{"t": 2348,"d": 8}])

        self.assertEqual(d.tshift(4)[0]["t"],2349)
        self.assertEqual(d[1]["t"],2352)

        self.assertEqual(d.sum(),53)
        self.assertEqual(d.mean(),53/2.0)

if __name__ == "__main__":
    unittest.main()
